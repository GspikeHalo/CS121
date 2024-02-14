#  .search_engine/engine/method.py

import sqlite3
import datetime
from method import Method
from raw_webpage import RawWebpageProcessor
from tokens import TokenProcessor
from inverted_index import InvertedIndexProcessor
from file_processor import RawWebpages, Log


class DatabaseProcessor:
    def __init__(self, update_time=100):
        self._db = None
        self._log = Log("../../database/db_log.txt")
        self._raw_pages = RawWebpages()
        self._raw_webpage_processor = RawWebpageProcessor()
        self._token_processor = TokenProcessor()
        self._inverted_index_processor = InvertedIndexProcessor()
        self._UPDATE_TIME = update_time

    def open_db(self, db_path="../../database/tf_idf_index.db"):
        self._ensure_database_exists(db_path)
        latest_log = self._log.get_latest_log()
        if latest_log:
            time, num = latest_log.strip().split(" ")
        else:
            time, num = None, None

        self._raw_pages.initialize_raw_webpage()
        if not time or not num or not Method.check_time_difference(time, self._UPDATE_TIME) or not Method.check_num_difference(self._raw_pages.get_len(), num):
            print("update")
            self._update_database()

    def get_db(self):
        return self._db

    def close_db(self):
        if self._db:
            self._db.close()

    def _ensure_database_exists(self, db_path):
        self._db = sqlite3.connect(db_path)
        self._initialize_db()

    def _initialize_db(self):
        self._raw_webpage_processor.init_raw_webpage(self._db)
        self._token_processor.init_tokens(self._db)
        self._inverted_index_processor.init_inverted_index(self._db)

    def _update_database(self):
        raw_webpage_num = self._raw_webpage_processor.update_raw_webpage(self._raw_pages.get_pages())
        for doc_id in self._raw_webpage_processor.get_all_doc_id():
            print(doc_id)
            folder_name, file_name = doc_id[0].split("/")
            content = self._raw_pages.load_raw_webpage_content(folder_name, file_name)
            token_weight = Method.calculate_token_weight(content.encode("utf-8"))
            self._token_processor.update_token(token_weight)
            self._inverted_index_processor.update_inverted_index(token_weight, doc_id[0])
        log = f"{datetime.datetime.now().date()} {raw_webpage_num}"
        self._log.update_log(log)


if __name__ == '__main__':
    db_processor = DatabaseProcessor()
    db_processor.open_db()
    db = db_processor.get_db()
    cursor = db.cursor()
    sql = "SELECT * FROM webpage"
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        # for row in result:
        #     print("doc_id:", row[0])
        #     print("  URL:", row[1])
    except Exception as e:
        print("Error:", e)
