#  .search_engine/engine/method.py

import sqlite3
import datetime
from method import Method
from raw_webpage import RawWebpageProcessor
from tokens import TokenProcessor
from inverted_index import InvertedIndexProcessor, TFIDFInfo
from file_processor import RawWebpages, Log


class DatabaseProcessor:
    def __init__(self, update_time: int = 100):
        self._db = None
        self._log = Log("../../database/db_log.txt")
        self._raw_webpage_processor = RawWebpageProcessor()
        self._token_processor = TokenProcessor()
        self._inverted_index_processor = InvertedIndexProcessor()
        self._UPDATE_TIME = update_time

    def open_db(self, raw_pages: RawWebpages, db_path: str = "../../database/tf_idf_index.db") -> None:
        self._ensure_database_exists(db_path)
        latest_log = self._log.get_latest_log()
        if latest_log:
            time, num = latest_log.strip().split(" ")
        else:
            time, num = None, None

        raw_pages.initialize_raw_webpage()
        if not time or not num or not Method.check_time_difference(time,
                                                                   self._UPDATE_TIME) or not Method.check_num_difference(
            raw_pages.get_len(), num):
            print("update")
            self._update_database(raw_pages)

            # 此处开始为测试程序，不需要可以注释掉，巨慢
            tf_idf_list = []
            n = self._raw_webpage_processor.get_total_length()
            for doc_id in self._raw_webpage_processor.get_all_doc_id():
                doc_id = doc_id[0]
                print(doc_id)
                d = self._raw_webpage_processor.get_total_words(doc_id)
                dict_tf_idf = {key: value for key, value in self._inverted_index_processor.get_word_num(doc_id)}
                for token in self._inverted_index_processor.get_token_by_doc_id(doc_id):
                    token = token[0]
                    f_td = dict_tf_idf[token]
                    n_t = self._token_processor.get_doc_num(token)
                    tf_idf = Method.calculate_tf_idf(f_td, d, n, n_t)
                    tf_idf_list.append(TFIDFInfo(token, doc_id, tf_idf))
                if len(tf_idf_list) >= 2000:
                    print("writing...")
                    self._inverted_index_processor.update_tf_idf(tf_idf_list)
                    tf_idf_list = []
            if tf_idf_list:
                self._inverted_index_processor.update_tf_idf(tf_idf_list)
        # for token, doc_id in self._inverted_index_processor.get_doc_id_and_token():
        #     print(doc_id)
        #     f_td = self._inverted_index_processor.get_tf_idf(token, doc_id)
        #     d = self._raw_webpage_processor.get_total_words(doc_id)
        #     n_t = self._token_processor.get_doc_num(token)
        #     tf_idf = Method.calculate_tf_idf(f_td, d, n, n_t)
        #     tf_idf_list.append(TFIDFInfo(token, doc_id, tf_idf))
        #     if len(tf_idf_list) >= 2000:
        #         self._inverted_index_processor.update_tf_idf(tf_idf_list)
        #         tf_idf_list = []
        # if tf_idf_list:
        #     self._inverted_index_processor.update_tf_idf(tf_idf_list)

    def get_db(self):
        return self._db

    def close_db(self) -> None:
        self._raw_webpage_processor.close()
        self._token_processor.close()
        self._inverted_index_processor.close()
        if self._db:
            self._db.close()

    def search_url(self, query: str) -> list[tuple]:
        return self._raw_webpage_processor.search_by_url(query)  # [("0/0", url, title, description)]

    def search_tokens(self, token: str) -> list[tuple]:  # 获取已经排序好的list of (doc_id, url)
        doc_ids = self._inverted_index_processor.search_by_tokens(token)
        doc_ids = sorted(doc_ids, key=lambda x: x[2])  # 根据tf_idf进行排序
        return doc_ids  # [(token01, "0/0", tf_idf), (token01, "0/1", tf_idf)]

    def search_doc_id(self, doc_id: str) -> list[tuple]:
        return self._raw_webpage_processor.search_by_doc_id(doc_id)

    def _ensure_database_exists(self, db_path: str) -> None:
        self._db = sqlite3.connect(db_path)
        self._initialize_db()

    def _initialize_db(self) -> None:
        self._raw_webpage_processor.init_raw_webpage(self._db)
        self._token_processor.init_tokens(self._db)
        self._inverted_index_processor.init_inverted_index(self._db)

    def _update_database(self, raw_pages: RawWebpages) -> None:
        raw_webpage_num = self._raw_webpage_processor.update_raw_webpage(raw_pages.get_pages())
        for doc_id in self._raw_webpage_processor.get_all_doc_id():
            print(doc_id)
            folder_name, file_name = Method.get_folder_num_and_file_num(doc_id[0])
            content = raw_pages.load_raw_webpage_content(folder_name, file_name)
            byte_content = content.encode("utf-8")
            token_weight = Method.calculate_token_weight(byte_content)
            title, first_sentence, word_num = Method.get_html_general_info(byte_content)
            self._raw_webpage_processor.update_webpage_info(doc_id[0], title, first_sentence, word_num, byte_content)
            self._token_processor.update_token(token_weight)
            self._inverted_index_processor.update_inverted_index(token_weight, doc_id[0])

        # n = self._raw_webpage_processor.get_total_length()
        # for token in self._token_processor.get_all_tokens():
        #     for doc_id in self._raw_webpage_processor.get_all_doc_id():
        #         token = token[0]
        #         doc_id = doc_id[0]
        #         f_td = self._inverted_index_processor.get_tf_idf(token, doc_id)
        #         d = self._raw_webpage_processor.get_total_words(doc_id)
        #         n_t = self._token_processor.get_doc_num(token)
        #         tf_idf = Method.calculate_tf_idf(f_td, d, n, n_t)
        #         self._inverted_index_processor.update_tf_idf(token, doc_id, tf_idf)
        log = f"{datetime.datetime.now().date()} {raw_webpage_num}"
        self._log.update_log(log)



if __name__ == '__main__':
    db_processor = DatabaseProcessor()
    raw_pages = RawWebpages()
    db_processor.open_db(raw_pages)
    db = db_processor.get_db()
    cursor = db.cursor()
    sql = "SELECT * FROM webpage"
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        for row in result:
            print("doc_id:", row[0])
            print("URL:", row[1])
            print("Title:", row[2])
            print("Description:", row[3])
    except Exception as e:
        print("Error:", e)
