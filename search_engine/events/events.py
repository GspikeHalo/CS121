#  search_engine/events/events.py

from search_engine.events.structure import WebpageGeneralInfo


class OpenDatabaseEvent:
    def __init__(self, db_path):
        self._db_path = db_path

    def get_db_path(self):
        return self._db_path


class DatabaseOpenEvent:
    pass


class CloseDatabaseEvent:
    pass


class DatabaseCloseEvent:
    pass


class SearchTokenEvent:
    def __init__(self, content: str):
        self._content = content

    def get_content(self) -> str:
        return self._content


class TokenSearchEvent:
    def __init__(self, content: list[WebpageGeneralInfo]):
        self._content = content

    def get_content(self) -> list[WebpageGeneralInfo]:
        return self._content


class SearchURLEvent:
    def __init__(self, content: str):
        self._content = content

    def get_content(self) -> str:
        return self._content


class URLSearchEvent:
    def __init__(self, content: list[WebpageGeneralInfo]):
        self._content = content

    def get_content(self) -> list[WebpageGeneralInfo]:
        return self._content
