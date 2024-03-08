#  .search_engine/engine/main.py

from search_engine.events.events import *
from search_engine.engine.database_processor import DatabaseProcessor
from search_engine.engine.file_processor import RawWebpages


class Engine:
    def __init__(self):
        self._db = DatabaseProcessor()
        self._raw_pages = RawWebpages()

    def process_event(self, event):
        if isinstance(event, SearchTokenEvent):
            return self._search_token_event(event)
        if isinstance(event, SearchURLEvent):
            return self._search_url_event(event)
        elif isinstance(event, OpenDatabaseEvent):
            return self._open_database_event(event)
        elif isinstance(event, CloseDatabaseEvent):
            return self._close_database_event()

    def _search_token_event(self, event: SearchTokenEvent) -> TokenSearchEvent:
        tokens = event.get_content()
        pages = self._db.search_tokens(tokens)
        result = [WebpageGeneralInfo(url=page[1], title=page[2], first_sentence=page[3]) for page in pages]
        print(len(result))
        return TokenSearchEvent(result)

    def _search_url_event(self, event: SearchURLEvent) -> URLSearchEvent:
        inquiry = event.get_content()
        pages = self._db.search_url(inquiry)  # InfoBridge
        result = [WebpageGeneralInfo(url=page[1], title=page[2], first_sentence=page[3]) for page in pages]
        return URLSearchEvent(result)

    def _open_database_event(self, event: OpenDatabaseEvent) -> DatabaseOpenEvent:
        path = event.get_db_path()
        self._raw_pages.set_root_path(path)
        self._db.open_db(self._raw_pages, path)
        return DatabaseOpenEvent()

    def _close_database_event(self) -> DatabaseCloseEvent:
        self._db.close_db()
        return DatabaseCloseEvent()


if __name__ == '__main__':
    engine = Engine()
    engine._open_database_event(OpenDatabaseEvent("../../"))
    while True:
        user_input = input("输入token：")  # 暂时没有错误处理，请勿输入错误url
        print(user_input)
        webpage_infos = engine.process_event(SearchTokenEvent(user_input))
        if not webpage_infos:
            print("NONONONO")
            continue
        for info in webpage_infos.get_content():
            print(
                f"web title: {info.get_title()}, web url: {info.get_url()}, web_first_sentence: {info.get_first_sentence()}")
