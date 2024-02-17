from collections import namedtuple

TFIDFInfo = namedtuple("TFIDFInfo", ("token", "doc_id", "tf_idf"))


class InvertedIndexProcessor:
    def __init__(self):
        self._db = None
        self._cursor = None

    def init_inverted_index(self, db) -> None:
        self._db = db
        self._cursor = db.cursor()
        sql = "CREATE TABLE IF NOT EXISTS inverted_index (token TEXT, doc_id TEXT, tf_idf REAL, word_num INT, FOREIGN KEY(token) REFERENCES tokens(token), FOREIGN KEY(doc_id) REFERENCES documents(doc_id))"
        self._db.execute(sql)
        self._db.commit()

    def update_inverted_index(self, token_weight: dict, doc_id: str) -> None:
        sql = "INSERT INTO inverted_index (token, doc_id, tf_idf, word_num) VALUES (?, ?, ?, ?)"

        for token, word_num in token_weight.items():
            self._cursor.execute(sql, (token, doc_id, None, word_num))
        self._db.commit()

    def update_tf_idf(self, info_list: list[TFIDFInfo]) -> None:
        # 准备SQL语句
        sql = "UPDATE inverted_index SET tf_idf=? WHERE token=? AND doc_id=?"
        # 构建参数列表
        params = [(info.tf_idf, info.token, info.doc_id) for info in info_list]
        # 开始事务
        self._cursor.execute('BEGIN')
        try:
            # 使用executemany批量执行更新
            self._cursor.executemany(sql, params)
            # 提交事务
            self._db.commit()
        except Exception as e:
            print("Error at i index", e)

    # def get_doc_id_and_token(self) -> list[tuple]:
    #     return self._cursor.execute("SELECT token, doc_id FROM inverted_index").fetchall()

    def get_token_by_doc_id(self, doc_id) -> list[tuple]:
        return self._cursor.execute("SELECT token FROM inverted_index WHERE doc_id=?", (doc_id,)).fetchall()

    def search_by_tokens(self, token: str) -> list[tuple]:
        self._cursor.execute("SELECT token, doc_id, tf_idf FROM inverted_index WHERE token=?", (token,))
        return self._cursor.fetchall()

    def get_word_num(self, doc_id: str) -> list[tuple]:
        self._cursor.execute("SELECT token, word_num FROM inverted_index WHERE doc_ID=?", (doc_id,))
        return self._cursor.fetchall()

    def close(self):
        if self._cursor:
            self._cursor.close()
        if self._db:
            self._db.close()
