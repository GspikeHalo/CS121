class TokenProcessor:
    def __init__(self):
        self._db = None
        self._cursor = None

    def init_tokens(self, db) -> None:
        self._db = db
        self._cursor = db.cursor()
        sql = "CREATE TABLE IF NOT EXISTS tokens (token TEXT PRIMARY KEY, doc_num INT, total_num INT)"
        self._cursor.execute(sql)
        self._db.commit()

    def update_token(self, token_weight: dict) -> None:
        try:
            self._db.execute("BEGIN")
            for token, total_num in token_weight.items():
                self._update_token_record(token, total_num)
            self._db.commit()
        except Exception as e:
            print(e)
            self._db.rollback()

    def get_all_tokens(self) -> list[tuple]:
        return self._cursor.execute("SELECT token FROM tokens").fetchall()

    def get_doc_num(self, token) -> int:
        return self._cursor.execute("SELECT doc_num FROM tokens WHERE token=?", (token,)).fetchone()[0]

    def close(self) -> None:
        if self._cursor:
            self._cursor.close()
        if self._db:
            self._db.close()

    def _update_token_record(self, token: int, total_num: int) -> bool:
        existing_record = self._cursor.execute("SELECT doc_num, total_num FROM tokens WHERE token = ?",
                                               (token,)).fetchone()
        if existing_record is None:
            self._cursor.execute("INSERT INTO tokens (token, doc_num, total_num) VALUES (?, ?, ?)",
                                 (token, 1, total_num))
        else:
            doc_num, existing_total_num = existing_record
            updated_total_num = existing_total_num + total_num
            self._cursor.execute("UPDATE tokens SET doc_num = ?, total_num = ? WHERE token = ?",
                                 (doc_num + 1, updated_total_num, token))
        return True
