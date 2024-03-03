from pymongo import MongoClient


class InvertedIndexDB:
    def __init__(self, db_name, collection_name):
        # 初始化MongoDB连接
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def bulk_update_tf_idf(self, tf_idf_data):
        # 执行批量写入操作
        # tf_idf_data 是一个列表，每个元素是一个包含token, docID和tf_idf值的字典
        for data in tf_idf_data:
            self.update_tf_idf(data['token'], data['doc_id'], data['tf_idf'], data['position'])

    def update_tf_idf(self, token: str, doc_id: str, tf_idf: float, position: list):
        # 检查是否已存在该token
        document = self.collection.find_one({"token": token})
        if document:
            # 构建新的文档信息，包含position
            new_document = {"docID": doc_id, "tf_idf": tf_idf, "position": position}
            # 检查文档是否已存在于列表中
            if not any(d["docID"] == doc_id for d in document["documents"]):
                # 如果文档不存在，则添加整个文档信息，包括位置信息
                self.collection.update_one({"token": token}, {"$push": {"documents": new_document}})
            else:
                # 如果文档已存在，更新TF-IDF值和位置信息
                self.collection.update_one(
                    {"token": token, "documents.docID": doc_id},
                    {
                        "$set": {
                            "documents.$.tf_idf": tf_idf,
                            "documents.$.position": position  # 更新位置信息
                        }
                    }
                )
        else:
            # 插入新token及其文档、TF-IDF值和位置信息
            new_entry = {
                "token": token,
                "documents": [
                    {
                        "docID": doc_id,
                        "tf_idf": tf_idf,
                        "position": position  # 添加位置信息
                    }
                ]
            }
            self.collection.insert_one(new_entry)

    def get_documents_by_token(self, token):
        # 根据token获取相关的documents
        result = self.collection.find_one({"token": token})
        if result:
            return result["documents"]
        else:
            return None
