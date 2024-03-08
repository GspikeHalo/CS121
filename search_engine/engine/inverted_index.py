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

    def get_sorted_doc_ids_by_token(self, token: str) -> list[str]:
        """
        Retrieves document IDs associated with a given token, sorted by their TF-IDF score in descending order.

        :param token: The token for which to retrieve sorted document IDs.
        :return: A list of document IDs associated with the token, sorted by TF-IDF score.
        """
        result = self.collection.find_one({"token": token})
        if result:
            documents = result["documents"]
            sorted_documents = sorted(documents, key=lambda d: d['tf_idf'], reverse=True)
            sorted_doc_ids = [d['docID'] for d in sorted_documents]
            return sorted_doc_ids
        else:
            return []

    def fetch_all_as_dict(self):
        """
        Fetches the entire collection and returns it as a dictionary.

        :return: A dictionary with tokens as keys and lists of documents as values.
        """
        inverted_index_dict = {}
        for document in self.collection.find():
            token = document["token"]
            documents_info = document.get("documents", [])
            inverted_index_dict[token] = documents_info
        return inverted_index_dict
