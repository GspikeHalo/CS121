from method import Method


class TokensWeight:
    def __init__(self):
        self._db = None
        self._cursor = None

    def init_tokens_weight(self, db) -> None:
        self._db = db
        self._cursor = db.cursor()
        sql = "CREATE TABLE IF NOT EXISTS tokens_weight (token TEXT, doc_id TEXT, word_num INT, position TEXT, FOREIGN KEY(token) REFERENCES tokens(token), FOREIGN KEY(doc_id) REFERENCES documents(doc_id))"
        self._db.execute(sql)
        self._db.commit()

    def update_tokens_weight(self, token_weight: dict, doc_id: str) -> None:
        sql = "INSERT INTO tokens_weight (token, doc_id, word_num, position) VALUES (?, ?, ?, ?)"

        for token, info in token_weight.items():
            word_num = info['weight']
            position = info['positions']
            position = Method.serialize_list_to_json(position)
            self._cursor.execute(sql, (token, doc_id, word_num, position))
        self._db.commit()

    def remove_duplicate(self, doc_ids: list):
        sql = "DELETE FROM tokens_weight WHERE doc_id = ?"
        self._db.execute("BEGIN")
        try:
            for doc_id in doc_ids:
                self._cursor.execute(sql, (doc_id,))
            self._db.commit()
        except Exception as e:
            print(f"Error removing duplicates: {e}")
            self._db.rollback()

    def get_token_by_doc_id(self, doc_id) -> list[tuple]:
        return self._cursor.execute("SELECT token FROM tokens_weight WHERE doc_id=?", (doc_id,)).fetchall()

    def get_word_num(self, doc_id: str) -> list[tuple]:
        self._cursor.execute("SELECT token, word_num FROM tokens_weight WHERE doc_ID=?", (doc_id,))
        return self._cursor.fetchall()

    def get_word_position(self, doc_id: str) -> list[tuple]:
        self._cursor.execute("SELECT token, position FROM tokens_weight WHERE doc_ID=?", (doc_id,))
        return self._cursor.fetchall()

    def close(self):
        if self._cursor:
            self._cursor.close()
        if self._db:
            self._db.close()

