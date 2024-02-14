class RawWebpageProcessor:
    def __init__(self):
        self._db = None
        self._cursor = None

    def init_raw_webpage(self, db):
        self._db = db
        self._cursor = db.cursor()
        sql = "CREATE TABLE IF NOT EXISTS webpage (doc_id TEXT PRIMARY KEY, URL TEXT)"
        self._cursor.execute(sql)
        self._db.commit()

    def update_raw_webpage(self, content: dict):
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

    def get_all_doc_id(self):
        self._cursor.execute("SELECT doc_id FROM webpage")
        return self._cursor.fetchall()

    def search_by_url(self, url):
        self._cursor.execute("SELECT doc_id, url FROM webpage WHERE url=?", (url,))
        return self._cursor.fetchall()

    def search_by_doc_id(self, doc_id):
        self._cursor.execute("SELECT doc_id, url FROM webpage WHERE doc_id=?", (doc_id,))
        return self._cursor.fetchall()

    def close(self):
        if self._cursor:
            self._cursor.close()
        if self._db:
            self._db.close()

    def _update_webpage_record(self, doc_id, url):
        existing_record = self._cursor.execute("SELECT * FROM webpage WHERE doc_id = ?", (doc_id,)).fetchone()
        if existing_record is None:
            self._cursor.execute("INSERT INTO webpage (doc_id, URL) VALUES (?, ?)", (doc_id, url))
        else:
            self._cursor.execute("UPDATE webpage SET URL = ? WHERE doc_id = ?", (url, doc_id))
        return True
