#  .search_engine/engine/tokens_weight.py

from method import Method


class TokensWeightProcessor:
    """
    Manages the storage, retrieval, and manipulation of tokens' weights and positions within tokens_weight
    table in a database.
    """

    def __init__(self):
        self._db = None

    def init_tokens_weight(self, db) -> None:
        """
        Initializes the database table for storing tokens' weights and positions if it doesn't already exist.

        :param db: The database connection object.
        :return: None
        """
        self._db = db
        sql = ("CREATE TABLE IF NOT EXISTS tokens_weight ("
               "token TEXT, "
               "doc_id TEXT, "
               "word_num INT, "
               "position TEXT, "
               "FOREIGN KEY(token) REFERENCES tokens(token), "
               "FOREIGN KEY(doc_id) REFERENCES documents(doc_id))"
               )
        self._db.execute(sql)
        self._db.commit()

    def update_tokens_weight(self, token_weight: dict, doc_id: str) -> None:
        """
        Inserts or updates tokens' weights and positions for a given document ID.

        :param token_weight: A dictionary where keys are tokens and values are dictionaries containing 'weight' and 'positions'.
        :param doc_id: The document ID to which the tokens belong.
        :return: None
        """
        cursor = self._db.cursor()
        sql = ("INSERT INTO tokens_weight "
               "(token, doc_id, word_num, position) "
               "VALUES (?, ?, ?, ?)"
               )
        for token, info in token_weight.items():
            word_num = info['weight']
            position = info['positions']
            position = Method.serialize_list_to_json(position)
            cursor.execute(sql, (token, doc_id, word_num, position))
        self._db.commit()
        cursor.close()

    def remove_duplicate(self, doc_ids: list) -> None:
        """
        Removes entries from the tokens_weight table for a list of document IDs, which have duplicate content.

        :param doc_ids: A list of document IDs for which to remove entries.
        :return: None
        """
        sql = "DELETE FROM tokens_weight WHERE doc_id = ?"
        self._db.execute("BEGIN")
        cursor = self._db.cursor()
        try:
            for doc_id in doc_ids:
                cursor.execute(sql, (doc_id,))
            self._db.commit()
        except Exception as e:
            print(f"Error removing duplicates: {e}")
            self._db.rollback()
        finally:
            cursor.close()

    def get_token_by_doc_id(self, doc_id) -> list[tuple]:
        """
        Fetches tokens for a given document ID.

        :param doc_id: The document ID.
        :return: A list of tuples, each containing a token.
        """
        cursor = self._db.cursor()
        result = cursor.execute("SELECT token FROM tokens_weight WHERE doc_id=?", (doc_id,)).fetchall()
        cursor.close()
        return result

    def get_word_num(self, doc_id: str) -> list[tuple]:
        """
        Fetches tokens and their frequencies for a given document ID.

        :param doc_id: The document ID.
        :return: A list of tuples, each containing a token and its weight (word_num).
        """
        cursor = self._db.cursor()
        result = cursor.execute("SELECT token, word_num FROM tokens_weight WHERE doc_ID=?", (doc_id,)).fetchall()
        cursor.close()
        return result

    def get_word_position(self, doc_id: str) -> list[tuple]:
        """
        Fetches tokens and their positions for a given document ID.

        :param doc_id: The document ID.
        :return: A list of tuples, each containing a token and its positions.
        """
        cursor = self._db.cursor()
        result = cursor.execute("SELECT token, position FROM tokens_weight WHERE doc_ID=?", (doc_id,)).fetchall()
        cursor.close()
        return result

    def close(self) -> None:
        """
        Closes the database connection if it's open.

        :return: None
        """
        if self._db:
            self._db.close()
