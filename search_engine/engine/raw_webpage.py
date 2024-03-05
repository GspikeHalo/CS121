#  .search_engine/engine/raw_webpage.py

class RawWebpageProcessor:
    """
    Manages the storage, retrieval, and manipulation of webpages within webpage table in a database.
    """

    def __init__(self):
        self._db = None

    def init_raw_webpage(self, db) -> None:
        """
        Initializes the webpage table in the database, creating it if it does not exist.

        :param db: The database connection object.
        :return: None
        """
        self._db = db
        sql = ("CREATE TABLE IF NOT EXISTS webpage ("
               "doc_id TEXT PRIMARY KEY, "
               "URL TEXT, "
               "title TEXT, "
               "description TEXT, "
               "total_words INT, "
               "corpus BLOB, "
               "vector TEXT)")
        self._db.execute(sql)
        self._db.commit()

    def update_raw_webpage(self, content: dict) -> int:
        """
        Updates the webpage records in the database based on the provided content dictionary.

        :param content: A dictionary containing the webpage url with document IDs as keys.
        :return: The number of updated records.
        """
        if not isinstance(content, dict):
            raise ValueError("content should be a dict object")

        self._db.execute("BEGIN")
        num = 0
        try:
            for doc_id, url in content.items():
                if self._update_webpage_record(doc_id, url):
                    num += 1
            self._db.commit()
            return num
        except Exception:
            self._db.rollback()
            return 0

    def update_webpage_info(self, doc_id: str, title: str, description: str, total_words: int, corpus: bytes) -> bool:
        """
        Updates specific information for a webpage record identified by the document ID.

        :param doc_id: The document ID of the webpage.
        :param title: The title of the webpage.
        :param description: The description of the webpage.
        :param total_words: The total number of words on the webpage.
        :param corpus: The raw content of the webpage as bytes.
        :return: True if the update was successful, False otherwise.
        """
        cursor = self._db.cursor()
        try:
            cursor.execute(
                "UPDATE webpage SET title = ?, description = ?, total_words = ?, corpus = ? WHERE doc_id = ?",
                (title, description, total_words, corpus, doc_id))
            self._db.commit()
            return True
        except Exception as e:
            print(f"Error updating webpage info: {e}")
            self._db.rollback()
            return False
        finally:
            cursor.close()

    def remove_duplicate(self) -> list:
        """
        Removes duplicate webpage records based on the corpus content.

        :return: A list of document IDs that were removed due to duplication.
        """
        duplicates_query = """
        SELECT doc_id
        FROM (
            SELECT doc_id,
                   ROW_NUMBER() OVER(PARTITION BY corpus ORDER BY doc_id) AS rn
            FROM webpage
        ) tmp
        WHERE rn > 1
        """
        cursor = self._db.cursor()
        try:
            self._db.execute("BEGIN")
            duplicates = cursor.execute(duplicates_query).fetchall()
            if not duplicates:
                self._db.commit()
                return []

            deleted_doc_ids = [dup[0] for dup in duplicates]
            delete_query = "DELETE FROM webpage WHERE doc_id = ?"
            for dup in deleted_doc_ids:
                cursor.execute(delete_query, (dup,))
            self._db.commit()
            return deleted_doc_ids
        except Exception as e:
            print(f"Error deduplicating by corpus: {e}")
            self._db.rollback()
            return []
        finally:
            cursor.close()

    def update_tf_idf(self, doc_id: str, vector: str) -> None:
        """
        Updates the TF-IDF vector representation for a specific webpage.

        :param doc_id: The document ID of the webpage.
        :param vector: The TF-IDF vector as a string.
        :return: None
        """
        cursor = self._db.cursor()
        sql = "UPDATE webpage SET vector = ? WHERE doc_id = ?"
        cursor.execute(sql, (vector, doc_id))
        cursor.close()
        self._db.commit()

    def get_all_doc_id(self) -> list[tuple]:
        """
        get all document IDs from the webpage table.

        :return: A list of tuples, each containing a document ID.
        """
        cursor = self._db.cursor()
        result = cursor.execute("SELECT doc_id FROM webpage").fetchall()
        cursor.close()
        return result

    def get_total_length(self) -> int:
        """
        Calculates the total number of webpage records in the database.

        :return: The total number of webpage records.
        """
        cursor = self._db.cursor()
        result = cursor.execute("SELECT COUNT(*) FROM webpage").fetchone()[0]
        return result

    def get_total_words(self, doc_id) -> int:
        """
        Retrieves the total word count for a specific webpage.

        :param doc_id: The document ID of the webpage.
        :return: The total word count of the webpage.
        """
        cursor = self._db.cursor()
        result = cursor.execute("SELECT total_words FROM webpage WHERE doc_id=?", (doc_id,)).fetchone()[0]
        cursor.close()
        return result

    def search_by_url(self, url: str) -> list[tuple]:
        cursor = self._db.cursor()
        result = cursor.execute("SELECT doc_id, url, title, description FROM webpage WHERE url=?", (url,)).fetchall()
        cursor.close()
        return result

    def search_by_doc_id(self, doc_id: str) -> list[tuple]:
        cursor = self._db.cursor()
        result = self._db.execute("SELECT doc_id, url, title, description FROM webpage WHERE doc_id=?",
                                  (doc_id,)).fetchall()
        cursor.close()
        return result

    def close(self) -> None:
        """
        Closes the database connection if it's open.

        :return: None
        """
        if self._db:
            self._db.close()

    def _update_webpage_record(self, doc_id: str, url: str) -> bool:
        """
        A private method to update or insert a webpage record based on document ID and URL.

        :param doc_id: The document ID of the webpage.
        :param url: The URL of the webpage.
        :return: True if the operation was successful, indicating the record was either updated or inserted.
        """
        cursor = self._db.cursor()
        existing_record = cursor.execute("SELECT * FROM webpage WHERE doc_id = ?", (doc_id,)).fetchone()
        if existing_record is None:
            cursor.execute(
                "INSERT INTO webpage (doc_id, URL, title, description, total_words, corpus, vector) VALUES (?, ?, NULL, NULL, NULL, NULL, NULL)",
                (doc_id, url))
        else:
            cursor.execute(
                "UPDATE webpage SET URL = ?, title = NULL, description = NULL, total_words = NULL, corpus = NULL, vector = NULL WHERE doc_id = ?",
                (url, doc_id))
        cursor.close()
        return True
