class TokenProcessor:
    def __init__(self):
        self._db = None

    def init_tokens(self, db) -> None:
        self._db = db
        sql = "CREATE TABLE IF NOT EXISTS tokens (token TEXT PRIMARY KEY, doc_num INT, total_num INT)"
        self._db.execute(sql)
        self._db.commit()

    def update_token(self, token_weight: dict) -> None:
        try:
            self._db.execute("BEGIN")
            for token, info in token_weight.items():
                total_num = info['weight']
                self._update_token_record(token, total_num)
            self._db.commit()
        except Exception as e:
            print("Error!!!!!", e)

    def remove_duplicate(self, token_weights: dict) -> None:
        cursor = self._db.cursor()
        try:
            self._db.execute("BEGIN")
            for token, info in token_weights.items():
                weight = info['weight']
                existing_record = cursor.execute(
                    "SELECT doc_num, total_num FROM tokens WHERE token = ?",
                    (token,)).fetchone()
                if existing_record:
                    doc_num, total_num = existing_record
                    updated_doc_num = max(0, doc_num - 1)
                    updated_total_num = max(0, total_num - weight)
                    cursor.execute(
                        "UPDATE tokens SET doc_num = ?, total_num = ? WHERE token = ?",
                        (updated_doc_num, updated_total_num, token))
            self._db.commit()
        except Exception as e:
            print(f"Error removing token entries: {e}")
            self._db.rollback()
        finally:
            cursor.close()

    def get_all_tokens(self) -> list[tuple]:
        cursor = self._db.cursor()
        result = cursor.execute("SELECT token FROM tokens").fetchall()
        cursor.close()
        return result

    def get_doc_num(self, token) -> int:
        cursor = self._db.cursor()
        result = cursor.execute("SELECT doc_num FROM tokens WHERE token=?", (token,)).fetchone()[0]
        cursor.close()
        return result

    def close(self) -> None:
        if self._db:
            self._db.close()

    def _update_token_record(self, token: int, total_num: int) -> bool:
        cursor = self._db.cursor
        existing_record = cursor.execute("SELECT doc_num, total_num FROM tokens WHERE token = ?",
                                               (token,)).fetchone()
        if existing_record is None:
            cursor.execute("INSERT INTO tokens (token, doc_num, total_num) VALUES (?, ?, ?)",
                                 (token, 1, total_num))
        else:
            doc_num, existing_total_num = existing_record
            updated_total_num = existing_total_num + total_num
            cursor.execute("UPDATE tokens SET doc_num = ?, total_num = ? WHERE token = ?",
                                 (doc_num + 1, updated_total_num, token))
        cursor.close()
        return True
