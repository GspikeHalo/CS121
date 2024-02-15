#  search_engine/events/events.py

from search_engine.engine.structure import WebpageGeneralInfo


class OpenDatabaseEvent:
    pass


class DatabaseOpenEvent:
    pass


class CloseDatabaseEvent:
    pass


class DatabaseCloseEvent:
    pass


class SearchTokenEvent:
    def __init__(self, content: list[str]):
        self._content = content

    def get_content(self) -> list[str]:
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
