#  .search_engine/engine/inverted_index.py

from pymongo import MongoClient


class InvertedIndexDB:
    """
    A class to manage the inverted index within a MongoDB database for efficient full-text searching.

    """

    def __init__(self, db_name, collection_name):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def update_tf_idf(self, token: str, doc_id: str, tf_idf: float, position: list) -> None:
        """
        Updates or inserts TF-IDF score and position information for a specific token and document ID.

        :param token: The token (word) for which the information is being updated.
        :param doc_id: The document ID associated with the token.
        :param tf_idf: The TF-IDF score of the token in the document.
        :param position: A list of positions where the token appears within the document.
        :return: None
        """
        document = self.collection.find_one({"token": token})
        if document:
            new_document = {"docID": doc_id, "tf_idf": tf_idf, "position": position}
            if not any(d["docID"] == doc_id for d in document["documents"]):
                self.collection.update_one({"token": token}, {"$push": {"documents": new_document}})
            else:
                self.collection.update_one(
                    {"token": token, "documents.docID": doc_id},
                    {
                        "$set": {
                            "documents.$.tf_idf": tf_idf,
                            "documents.$.position": position
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
                        "position": position
                    }
                ]
            }
            self.collection.insert_one(new_entry)

    def get_documents_by_token(self, token: str) -> list[dict]:
        """
        Retrieves documents associated with a given token.

        :param token: The token for which to retrieve documents.
        :return: A list of documents associated with the token, or empty list if the token is not found.
        """
        result = self.collection.find_one({"token": token})
        if result:
            return result["documents"]
        else:
            return []
