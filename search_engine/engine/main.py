#  .search_engine/engine/main.py

from ..events import *
from .databaseprocessor import DatabaseProcessor


class Engine:
    def __init__(self):
        self._db = DatabaseProcessor()

    def process_event(self, event):
        if isinstance(event, SearchTokenEvent):
            yield self.start_search_event(event)
        elif isinstance(event, OpenDatabaseEvent):
            yield self.open_database_event()
        elif isinstance(event, CloseDatabaseEvent):
            yield self.close_database_event()

    def start_search_event(self, event: SearchTokenEvent):
        content = event.get_content()
        result = self._db.search_tokens(content) # 需要对该方法进行修改


    def open_database_event(self):
        self._db.open_db()
        return DatabaseOpenEvent()

    def close_database_event(self):
        self._db.close_db()
        return DatabaseCloseEvent()
