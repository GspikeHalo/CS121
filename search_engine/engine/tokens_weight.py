from method import Method


class TokensWeight:
    def __init__(self):
        self._db = None

    def init_tokens_weight(self, db) -> None:
        self._db = db
        sql = "CREATE TABLE IF NOT EXISTS tokens_weight (token TEXT, doc_id TEXT, word_num INT, position TEXT, FOREIGN KEY(token) REFERENCES tokens(token), FOREIGN KEY(doc_id) REFERENCES documents(doc_id))"
        self._db.execute(sql)
        self._db.commit()

    def update_tokens_weight(self, token_weight: dict, doc_id: str) -> None:
        cursor = self._db.cursor()
        sql = "INSERT INTO tokens_weight (token, doc_id, word_num, position) VALUES (?, ?, ?, ?)"
        for token, info in token_weight.items():
            word_num = info['weight']
            position = info['positions']
            position = Method.serialize_list_to_json(position)
            cursor.execute(sql, (token, doc_id, word_num, position))
        self._db.commit()
        cursor.close()

    def remove_duplicate(self, doc_ids: list):
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
        cursor = self._db.cursor()
        result = cursor.execute("SELECT token FROM tokens_weight WHERE doc_id=?", (doc_id,)).fetchall()
        cursor.close()
        return result

    def get_word_num(self, doc_id: str) -> list[tuple]:
        cursor = self._db.cursor()
        result = cursor.execute("SELECT token, word_num FROM tokens_weight WHERE doc_ID=?", (doc_id,)).fetchall()
        cursor.close()
        return result

    def get_word_position(self, doc_id: str) -> list[tuple]:
        cursor = self._db.cursor()
        result = cursor.execute("SELECT token, position FROM tokens_weight WHERE doc_ID=?", (doc_id,)).fetchall()
        cursor.close()
        return result

    def close(self):
        if self._db:
            self._db.close()

