#  .search_engine/engine/main.py

from search_engine.events import *
from search_engine.engine.database_processor import DatabaseProcessor
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

    def search_token_event(self, event: SearchTokenEvent) -> TokenSearchEvent:
        tokens = event.get_content()
        pages = self._db.search_tokens(tokens)
        result = [WebpageGeneralInfo(url=page[1], title=page[2], first_sentence=page[3]) for page in pages]
        return TokenSearchEvent(result)

    def search_url_event(self, event: SearchURLEvent) -> URLSearchEvent:
        inquiry = event.get_content()
        pages = self._db.search_url(inquiry)  # InfoBridge
        result = [WebpageGeneralInfo(url=page[1], title=page[2], first_sentence=page[3]) for page in pages]
        return URLSearchEvent(result)  # 后续添加分页机制，我认为可以通过dict，dict的key为页数，value为list of result

    def open_database_event(self) -> DatabaseOpenEvent:
        self._db.open_db(self._raw_pages)
        return DatabaseOpenEvent()

    def close_database_event(self) -> DatabaseCloseEvent:
        self._db.close_db()
        return DatabaseCloseEvent()


if __name__ == '__main__':
    engine = Engine()
    engine.open_database_event()
    while True:
        user_input = input("输入token：")  # 暂时没有错误处理，请勿输入错误url
        print(user_input)
        for webpage_infos in engine.process_event(SearchTokenEvent(user_input)):
            if not webpage_infos:
                print("NONONONO")
                continue
            for info in webpage_infos.get_content():
                print(
                    f"web title: {info.get_title()}, web url: {info.get_url()}, web_first_sentence: {info.get_first_sentence()}")
