import sqlite3
from structure import TFIDFInfo


class WeightMatrix:
    def __init__(self):
        self._db = None
        self._cursor = None

    def init_weight_matrix(self, db, doc_ids) -> None:
        self._db = db
        self._cursor = db.cursor()
        columns = ', '.join([f'"{doc_id[0]}" REAL' for doc_id in doc_ids])
        sql = f"CREATE TABLE IF NOT EXISTS weight_matrix (token TEXT PRIMARY KEY, {columns})"
        self._db.execute(sql)
        self._db.commit()

    def add_tokens(self, tokens: list[tuple]):
        # 构建SQL语句以插入新的token，所有文档列的值初始化为0
        columns = ', '.join([f'"{doc_id}"' for doc_id in self.doc_ids])
        placeholders = ', '.join(['?'] * (len(self.doc_ids) + 1))  # +1 for token column
        zero_values = [0] * len(self.doc_ids)  # 初始化所有文档列的值为0
        sql = f"INSERT INTO weight_matrix (token, {columns}) VALUES ({placeholders}) ON CONFLICT(token) DO NOTHING"
        for token in tokens:
            values = [token[0]] + zero_values
            self._cursor.execute(sql, values)
        self._db.commit()

    def update_tf_idf(self, info_list: list[TFIDFInfo]) -> None:
        self._cursor.execute('BEGIN')
        try:
            for info in info_list:
                # 检查是否存在记录
                check_sql = f"SELECT EXISTS(SELECT 1 FROM weight_matrix WHERE token=? LIMIT 1)"
                self._cursor.execute(check_sql, (info.token,))
                exists = self._cursor.fetchone()[0]
                if exists:
                    # 更新现有记录
                    update_sql = f"UPDATE weight_matrix SET {info.doc_id}=? WHERE token=?"
                    self._cursor.execute(update_sql, (info.tf_idf, info.token))
            self._db.commit()
        except Exception as e:
            # 如果出现异常，回滚事务
            self._db.rollback()
            print("Error during database operation:", e)

