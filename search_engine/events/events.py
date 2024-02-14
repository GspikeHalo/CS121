#  search_engine/events/events.py

from ..engine.structure import TokenStructure


class OpenDatabaseEvent:
    pass


class DatabaseOpenEvent:
    pass


class CloseDatabaseEvent:
    pass


class DatabaseCloseEvent:
    pass


class SearchTokenEvent:
    def __init__(self, content: list):
        self._content = content

    def get_content(self) -> list:
        return self._content


class TokenSearchEvent:
    def __init__(self, content: list[TokenStructure]):
        self._content = content

    def get_content(self) -> list[TokenStructure]:
        return self._content


class SearchURLEvent:
    def __init__(self, content: str):
        self._content = content

    def get_content(self) -> str:
        return self._content


class URLSearchEvent:
    def __init__(self, content: list):
        self._content = content

    def get_content(self) -> list:
        return self._content
