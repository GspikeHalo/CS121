#  .search_engine/engine/database_processor.py

import sqlite3
import datetime
import functools
from method import Method
from raw_webpage import RawWebpageProcessor
from tokens import TokenProcessor
from tokens_weight import TokensWeightProcessor
from file_processor import RawWebpages, Log
from inverted_index import InvertedIndexDB
from connection_pool import SQLiteConnectionPool
from concurrent.futures import ThreadPoolExecutor

THREAD_NUM = 15

class DatabaseProcessor:
    def __init__(self, update_time: int = 100):
        self._db = None
        self._log = Log("../../database/db_log.txt")
        self._raw_webpage_processor = RawWebpageProcessor()
        self._token_processor = TokenProcessor()
        self._tokens_weight_processor = TokensWeightProcessor()
        self._pool = SQLiteConnectionPool("../../database/tf_idf_index.db", pool_size=THREAD_NUM)
        self._inverted_index_db = InvertedIndexDB("CS121", "inverted_index")
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
            # self._update_database(raw_pages)
            # self._remove_duplicate()
            # self._update_tf_idf()


    def get_db(self):
        return self._db

    def close_db(self) -> None:
        self._raw_webpage_processor.close()
        self._token_processor.close()
        self._tokens_weight_processor.close()
        if self._db:
            self._db.close()

    def search_url(self, query: str) -> list[tuple]:
        return self._raw_webpage_processor.search_by_url(query)  # [("0/0", url, title, description)]

    # def search_tokens(self, token: str) -> list[tuple]:  # 获取已经排序好的list of (doc_id, url)  # 进行修改
    #     doc_ids = self._inverted_index_processor.search_by_tokens(token)
    #     doc_ids = sorted(doc_ids, key=lambda x: x[2])  # 根据tf_idf进行排序
    #     return doc_ids  # [(token01, "0/0", tf_idf), (token01, "0/1", tf_idf)]

    def search_doc_id(self, doc_id: str) -> list[tuple]:
        return self._raw_webpage_processor.search_by_doc_id(doc_id)

    def _ensure_database_exists(self, db_path: str) -> None:
        self._db = sqlite3.connect(db_path, timeout=30)
        self._initialize_db()

    def _initialize_db(self) -> None:
        self._raw_webpage_processor.init_raw_webpage(self._db)
        self._token_processor.init_tokens(self._db)
        self._tokens_weight_processor.init_tokens_weight(self._db)
        # self._weight_matrix.init_db(self._db)

    def _update_database(self, raw_pages: RawWebpages) -> None:
        raw_webpage_num = self._raw_webpage_processor.update_raw_webpage(raw_pages.get_pages())
        doc_ids = self._raw_webpage_processor.get_all_doc_id()
        for doc_id in doc_ids:
            print(doc_id[0])
            folder_name, file_name = Method.get_folder_num_and_file_num(doc_id[0])
            content = raw_pages.load_raw_webpage_content(folder_name, file_name)
            byte_content = content.encode("utf-8")
            token_info = Method.calculate_token_weight(byte_content)
            title, first_sentence, word_num = Method.get_html_general_info(byte_content)
            self._raw_webpage_processor.update_webpage_info(doc_id[0], title, first_sentence, word_num, byte_content)
            self._token_processor.update_token(token_info)
            self._tokens_weight_processor.update_tokens_weight(token_info, doc_id[0])
        log = f"{datetime.datetime.now().date()} {raw_webpage_num}"
        self._log.update_log(log)

    def _remove_duplicate(self):
        duplicate_ids = self._raw_webpage_processor.remove_duplicate()
        self._tokens_weight_processor.remove_duplicate(duplicate_ids)
        for doc_id in duplicate_ids:
            print(doc_id)
            folder_name, file_name = Method.get_folder_num_and_file_num(doc_id)
            content = raw_pages.load_raw_webpage_content(folder_name, file_name)
            byte_content = content.encode("utf-8")
            token_info = Method.calculate_token_weight(byte_content)
            self._token_processor.remove_duplicate(token_info)

    def calculate_and_update_tf_idf(self, doc_id, original_dict_keys):
        db_connection = self._pool.get_connection()
        doc_vector_dict = {key: 0 for key in original_dict_keys}
        try:
            local_raw_webpage_processor = RawWebpageProcessor()
            local_tokens_weight_processor = TokensWeightProcessor()
            local_token_processor = TokenProcessor()
            local_raw_webpage_processor.init_raw_webpage(db_connection)
            local_tokens_weight_processor.init_tokens_weight(db_connection)
            local_token_processor.init_tokens(db_connection)

            print(doc_id)
            d = local_raw_webpage_processor.get_total_words(doc_id)
            dict_tf_idf = {key: value for key, value in local_tokens_weight_processor.get_word_num(doc_id)}
            dict_position = {key: position for key, position in local_tokens_weight_processor.get_word_position(doc_id)}

            for token in local_tokens_weight_processor.get_token_by_doc_id(doc_id):
                token = token[0]
                f_td = dict_tf_idf[token]
                n_t = local_token_processor.get_doc_num(token)
                n = local_raw_webpage_processor.get_total_length()
                tf_idf = Method.calculate_tf_idf(f_td, d, n, n_t)
                doc_vector_dict[token] = tf_idf
                position = dict_position[token]
                position = Method.deserialize_json_to_list(position)
                self._inverted_index_db.update_tf_idf(token, doc_id, tf_idf, position)
            doc_vector = doc_vector_dict.values()
            doc_vector = list(doc_vector)
            local_raw_webpage_processor.update_tf_idf(doc_id, Method.serialize_list_to_json(doc_vector))
        except Exception as e:
            print(e)
        finally:
            self._pool.release_connection(db_connection)

    def _update_tf_idf(self):
        doc_ids = [doc_id[0] for doc_id in self._raw_webpage_processor.get_all_doc_id()]
        original_keys = [token[0] for token in self._token_processor.get_all_tokens()]
        try:
            with ThreadPoolExecutor(max_workers=THREAD_NUM) as executor:
                func = functools.partial(self.calculate_and_update_tf_idf, original_dict_keys=original_keys)
                executor.map(func, doc_ids)
        finally:
            self._pool.close_all_connections()


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
        print('1')

        db_processor.close_db()
    except Exception as e:
        print("Error:", e)
