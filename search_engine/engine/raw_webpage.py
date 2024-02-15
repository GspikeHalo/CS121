class RawWebpageProcessor:
    def __init__(self):
        self._db = None
        self._cursor = None

    def init_raw_webpage(self, db) -> None:
        self._db = db
        self._cursor = db.cursor()
        sql = "CREATE TABLE IF NOT EXISTS webpage (doc_id TEXT PRIMARY KEY, URL TEXT, title TEXT, description TEXT)"
        self._cursor.execute(sql)
        self._db.commit()

    def update_raw_webpage(self, content: dict) -> int:
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

    def update_webpage_info(self, doc_id: str, title: str, description: str) -> bool:
        try:
            self._db.execute("UPDATE webpage SET title = ?, description = ? WHERE doc_id = ?",
                             (title, description, doc_id))
            self._db.commit()
            return True
        except Exception as e:
            print(f"Error updating webpage info: {e}")
            self._db.rollback()
            return False

    def get_all_doc_id(self) -> list[tuple]:
        self._cursor.execute("SELECT doc_id FROM webpage")
        return self._cursor.fetchall()

    def search_by_url(self, url: str) -> list[tuple]:
        self._cursor.execute("SELECT doc_id, url FROM webpage WHERE url=?", (url,))
        return self._cursor.fetchall()

    def search_by_doc_id(self, doc_id: str) -> list[tuple]:
        self._cursor.execute("SELECT doc_id, url FROM webpage WHERE doc_id=?", (doc_id,))
        return self._cursor.fetchall()

    def close(self) -> None:
        if self._cursor:
            self._cursor.close()
        if self._db:
            self._db.close()

    def _update_webpage_record(self, doc_id: str, url: str) -> bool:
        existing_record = self._cursor.execute("SELECT * FROM webpage WHERE doc_id = ?", (doc_id,)).fetchone()
        if existing_record is None:
            self._cursor.execute("INSERT INTO webpage (doc_id, URL, title, description) VALUES (?, ?, NULL, NULL)",
                                 (doc_id, url))
        else:
            self._cursor.execute("UPDATE webpage SET URL = ?, title = NULL, description = NULL WHERE doc_id = ?",
                                 (url, doc_id))
        return True


