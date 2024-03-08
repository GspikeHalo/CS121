#  .search_engine/engine/database_processor.py

import os
import sqlite3
import datetime
import functools
import heapq
from search_engine.engine.method import Method
from search_engine.engine.raw_webpage import RawWebpageProcessor
from search_engine.engine.tokens import TokenProcessor
from search_engine.engine.tokens_weight import TokensWeightProcessor
from search_engine.engine.file_processor import RawWebpages, Log
from search_engine.engine.inverted_index import InvertedIndexDB
from search_engine.engine.connection_pool import SQLiteConnectionPool
from concurrent.futures import ThreadPoolExecutor

THREAD_NUM = 10


class DatabaseProcessor:
    """
    A class that manages the entire database. Manage all database-related transactions.
    """

    def __init__(self, update_time: int = 100):
        self._db = None
        self._log = None
        self._raw_webpage_processor = RawWebpageProcessor()
        self._token_processor = TokenProcessor()
        self._tokens_weight_processor = TokensWeightProcessor()
        self._pool = None
        self._inverted_index_db = InvertedIndexDB("CS121SearchEngine", "inverted_index")
        self._inverted_index = None
        self._UPDATE_TIME = update_time

    def open_db(self, raw_pages: RawWebpages, db_path: str = "../../") -> None:
        """
        Initialize all database processors. If the condition is met, these databases are initialized.

        :param raw_pages: An instance that stores doc id and URL information
        :param db_path: Database root directory
        :return: None
        """
        database_path = os.path.join(db_path, "database/tf_idf_index.db")
        self._ensure_database_exists(database_path)
        self._log = Log(os.path.join(db_path, "database/db_log.txt"))
        self._pool = SQLiteConnectionPool(database_path, pool_size=THREAD_NUM)
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
            self._remove_duplicate(raw_pages)
            self._update_tf_idf()
        self._inverted_index = self._inverted_index_db.fetch_all_as_dict()

    def get_db(self):
        """
        Fetching the database

        :return: The database currently in use
        """
        return self._db

    def close_db(self) -> None:
        self._raw_webpage_processor.close()
        self._token_processor.close()
        self._tokens_weight_processor.close()
        if self._db:
            self._db.close()

    def search_url(self, query: str) -> list[tuple]:
        """
        Based on the URL entered, search the database

        :param query: The URL to query
        :return: Search results
        """
        print("in URL")
        return self._raw_webpage_processor.search_by_url(query)  # [("0/0", url, title, description)]

    def search_tokens(self, query: str) -> list[tuple]:
        """
        Based on the query entered, search the database

        :param query: Input query
        :return: Search results
        """
        result = []
        tokens = Method.preprocess_text(query)
        if len(tokens) > 1:
            print("in multi tokens")
            query_vector = self._get_query_vector(tokens)
            sorted_doc_ids = self._process_tokens(tokens, query_vector)
        elif len(tokens) == 1:
            print("in single tokens")
            sorted_doc_ids = self._inverted_index_db.get_sorted_doc_ids_by_token(query[0])
        else:
            sorted_doc_ids = []
        for doc_id in sorted_doc_ids:
            doc_result = self._raw_webpage_processor.search_by_doc_id(doc_id)
            if len(result) + len(doc_result) > 50:
                result.extend(doc_result[:50 - len(result)])
                break
            else:
                result.extend(doc_result)
        return result

    def _ensure_database_exists(self, db_path: str) -> None:
        """
        Connect to the database and initialize the tables

        :param db_path: Database root directory
        :return: None
        """
        self._db = sqlite3.connect(db_path, timeout=30)
        self._initialize_db()

    def _initialize_db(self) -> None:
        """
        Initialize the tables

        :return: None
        """
        self._raw_webpage_processor.init_raw_webpage(self._db)
        self._token_processor.init_tokens(self._db)
        self._tokens_weight_processor.init_tokens_weight(self._db)

    def _update_database(self, raw_pages: RawWebpages) -> None:
        """
        Save the updated content into the database

        :param raw_pages: An instance that stores doc id and URL information
        :return: None
        """
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

    def _remove_duplicate(self, raw_pages: RawWebpages) -> None:
        """
        Remove duplicate data from the database

        :param raw_pages: An instance that stores doc id and URL information
        :return: None
        """
        duplicate_ids = self._raw_webpage_processor.remove_duplicate()
        self._tokens_weight_processor.remove_duplicate(duplicate_ids)
        for doc_id in duplicate_ids:
            print(doc_id)
            folder_name, file_name = Method.get_folder_num_and_file_num(doc_id)
            content = raw_pages.load_raw_webpage_content(folder_name, file_name)
            byte_content = content.encode("utf-8")
            token_info = Method.calculate_token_weight(byte_content)
            self._token_processor.remove_duplicate(token_info)

    def _calculate_and_update_tf_idf(self, doc_id):
        """
        Calculate tf-idf for all tokens in a single file

        :param doc_id: doc id of the file
        :return: None
        """
        db_connection = self._pool.get_connection()

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
                position = dict_position[token]
                position = Method.deserialize_json_to_list(position)
                self._inverted_index_db.update_tf_idf(token, doc_id, tf_idf, position)
        except Exception as e:
            print(e)
        finally:
            self._pool.release_connection(db_connection)

    def _update_tf_idf(self):
        """
        Update inverted index, including position, tf-idf.

        :return: None
        """
        doc_ids = [doc_id[0] for doc_id in self._raw_webpage_processor.get_all_doc_id()]
        try:
            with ThreadPoolExecutor(max_workers=THREAD_NUM) as executor:
                executor.map(self._calculate_and_update_tf_idf, doc_ids)
        finally:
            self._pool.close_all_connections()

    def _get_query_vector(self, tokens: list[str]) -> dict:
        """
        Calculate the tf-idf for each word in the query

        :param tokens: Each token in the query
        :return: A dictionary containing the tf-idf of each token
        """
        d = len(tokens)
        n = self._raw_webpage_processor.get_total_length() + 1
        token_counts = {}
        for token in tokens:
            if token in token_counts:
                token_counts[token] += 1
            else:
                token_counts[token] = 1

        dict_tf_idf = {}
        for token in tokens:
            f_td = token_counts[token]
            n_t = self._token_processor.get_doc_num(token) + 1
            tf_idf = Method.calculate_tf_idf(f_td, d, n, n_t)
            dict_tf_idf[token] = tf_idf
        return dict_tf_idf

    def _process_tokens(self, query: list, query_dict: dict) -> list:
        """
        The file score is obtained by calculating the cosine similarity and location information of each file.
        And pick the first 50 to return

        :param query: Query
        :param query_dict: tf-idf for each token of the query
        :return:
        """
        scores = {}
        doc_lengths = {}
        phrase_bonus = 2.0
        processed_tokens = set()
        doc_positions = {}

        for i, token in enumerate(query):
            if token not in self._inverted_index:
                continue
            wt_q = query_dict[token]
            postings_list = self._inverted_index[token]
            for doc_info in postings_list:
                doc_id = doc_info['docID']
                wt_d = doc_info['tf_idf']
                positions = doc_info["position"]
                if doc_id not in doc_positions:
                    doc_positions[doc_id] = []
                doc_positions[doc_id].append(positions)

                if token in processed_tokens:
                    continue
                if doc_id not in scores:
                    scores[doc_id] = 0
                    doc_lengths[doc_id] = 0
                scores[doc_id] += wt_d * wt_q
                doc_lengths[doc_id] += wt_d ** 2
            processed_tokens.add(token)

        for doc_id, positions_list in doc_positions.items():
            if len(positions_list) > 1:
                for i in range(len(positions_list) - 1):
                    for pos in positions_list[i]:
                        if any(pos + 1 == next_pos for next_pos in positions_list[i + 1]):
                            scores[doc_id] += phrase_bonus
                            break

        # Length Normalization
        for doc_id in scores:
            if doc_lengths[doc_id] > 0:
                doc_length = doc_lengths[doc_id] ** 0.5
                scores[doc_id] /= doc_length

        top_50_doc_ids = heapq.nlargest(50, scores, key=scores.get)
        print(top_50_doc_ids)
        return top_50_doc_ids


if __name__ == '__main__':
    try:
        db_processor = DatabaseProcessor()
        raw_pages = RawWebpages()
        raw_pages.set_root_path()

        db_processor.open_db(raw_pages)
        db = db_processor.get_db()
        cursor = db.cursor()
        # print("1")
        # print("start search")
        # result = db_processor.search_tokens("ics major")
        # print(result)
        print('Finish Update Database')
        db_processor.close_db()
    except Exception as e:
        print("Error:", e)
