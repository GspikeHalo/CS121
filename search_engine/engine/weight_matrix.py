import sqlite3
from structure import TFIDFInfo
from table_range import TableRange


class WeightMatrix:
    def __init__(self):
        self._db = None
        self._cursor = None
        self._table_range_processor = TableRange()

    def init_db(self, db):
        self._db = db
        self._cursor = db.cursor()

    def init_weight_matrix(self, doc_ids: list[tuple]) -> None:
        batch_size = 1500
        table_index = 0
        temp_list = []

        doc_ids = sorted(doc_ids, key=lambda x: tuple(map(int, x[0].split('/'))))

        for i in range(0, len(doc_ids), batch_size):
            batch_doc_ids = doc_ids[i:i + batch_size]
            print(f"process {batch_doc_ids}")
            table_name = f"weight_matrix_{table_index}"
            self._cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (token TEXT PRIMARY KEY, query REAL)")
            self._db.commit()

            self._cursor.execute(f"PRAGMA table_info({table_name});")
            existing_columns = {info[1] for info in self._cursor.fetchall()}

            for doc_id in batch_doc_ids:
                # column_name = doc_id[0].replace('/', '_')  # 用下划线替换斜杠以避免SQL语法问题
                column_name = doc_id[0]
                if column_name not in existing_columns:
                    sql = f"ALTER TABLE {table_name} ADD COLUMN '{column_name}' REAL"
                    self._cursor.execute(sql)
                    self._db.commit()
            temp_list.append((table_name, batch_doc_ids[0][0], batch_doc_ids[-1][0]))
            table_index += 1
        self._table_range_processor.update_table_ranges(temp_list)

    def update_tokens(self, tokens: list[tuple]) -> None: # 修改
        for table_name, start_doc_id, end_doc_id in self._table_range_processor.get_table_ranges():
            print(f"updating table {table_name}")
            self._cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = self._cursor.fetchall()
            columns = [f'"{info[1]}"' for info in columns_info if info[1] != 'token']
            placeholders = ', '.join(['?'] * len(columns_info))
            zero_values = [0] * (len(columns_info) - 1)
            sql = f"INSERT INTO {table_name} (token, {', '.join(columns)}) VALUES ({placeholders})"
            for token in tokens:
                values = [token[0]] + zero_values
                self._cursor.execute(sql, values)
        self._db.commit()

    def update_tf_idf(self, doc_id: str, tf_idf_list: list[tuple]) -> None:
        table_name = self._table_range_processor.get_table_name_for_doc_id(doc_id)

        # column_name = doc_id.replace('/', '_')
        column_name = doc_id

        self._cursor.execute('BEGIN IMMEDIATE')
        for token, tf_idf_value in tf_idf_list:
            self._cursor.execute(f"SELECT EXISTS(SELECT 1 FROM {table_name} WHERE token=? LIMIT 1)", (token,))
            exists = self._cursor.fetchone()[0]
            if exists:
                update_sql = f"UPDATE {table_name} SET '{column_name}' = ? WHERE token = ?"
                self._cursor.execute(update_sql, (tf_idf_value, token))
        self._db.commit()
