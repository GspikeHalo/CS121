class InvertedIndexProcessor:
    def __init__(self):
        self._db = None
        self._cursor = None

    def init_inverted_index(self, db):
        self._db = db
        self._cursor = db.cursor()
        sql = "CREATE TABLE IF NOT EXISTS inverted_index (token TEXT, doc_id TEXT, tf_idf REAL, FOREIGN KEY(token) REFERENCES tokens(token), FOREIGN KEY(doc_id) REFERENCES documents(doc_id))"
        self._db.execute(sql)
        self._db.commit()

    def update_inverted_index(self, token_weight, doc_id):
        sql = "INSERT INTO inverted_index (token, doc_id, tf_idf) VALUES (?, ?, ?)"

        for token, tf_idf in token_weight.items():
            self._cursor.execute(sql, (token, doc_id, tf_idf))
        self._db.commit()
