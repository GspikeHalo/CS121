#  .search_engine/engine/main.py

from search_engine.events import *
from search_engine.engine.databaseprocessor import DatabaseProcessor
from method import Method
from file_processor import RawWebpages


class Engine:
    def __init__(self):
        self._db = DatabaseProcessor()
        self._raw_pages = RawWebpages()

    def process_event(self, event):
        if isinstance(event, SearchTokenEvent):
            yield self.search_token_event(event)
        if isinstance(event, SearchURLEvent):
            yield self.search_url_event(event)
        elif isinstance(event, OpenDatabaseEvent):
            yield self.open_database_event()
        elif isinstance(event, CloseDatabaseEvent):
            yield self.close_database_event()

    def search_token_event(self, event: SearchTokenEvent):
        # inquiry = event.get_content()
        # pages = self._db.search_tokens(inquiry)  # 需要对该方法进行修改 返回已经排好序的list of (doc_id, url)
        # result = self._get_webpage_info(pages)
        # return TokenSearchEvent([])
        pass

    def search_url_event(self, event: SearchURLEvent):
        inquiry = event.get_content()
        print(inquiry)
        pages = self._db.search_url(inquiry)  # list of (doc_id, rul)
        result = self._get_webpage_info(pages)
        return URLSearchEvent(result)  # 后续添加分页机制，我认为可以通过dict，dict的key为页数，value为list of result

    def open_database_event(self):
        self._db.open_db(self._raw_pages)
        return DatabaseOpenEvent()

    def close_database_event(self):
        self._db.close_db()
        return DatabaseCloseEvent()

    def _get_webpage_info(self, pages: list[tuple]):
        result = []
        for doc_id, url in pages:
            a = [doc_id]
            print(a)
            folder_num, file_num = Method.get_folder_num_and_file_num(a)  # Method.get_folder_num_and_file_num(doc_id)
            single_page = Method.get_html_general_info(
                self._raw_pages.load_raw_webpage_content(folder_num, file_num))
            single_page.set_url(url)
            result.append(single_page)
        return result


if __name__ == '__main__':
    engine = Engine()
    engine.open_database_event()
    while True:
        user_input = input("输入url：")  # 暂时没有错误处理，请勿输入错误url
        for webpage_infos in engine.process_event(SearchURLEvent(user_input)):
            for info in webpage_infos.get_content():
                print(f"web title: {info.get_title()}, web url: {info.get_url()}, web_first_sentence: {info.get_first_sentence()}")
