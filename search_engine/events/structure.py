#  .search_engine/engine/structure.py

from collections import namedtuple

# Define a namedtuple 'TFIDFInfo' for storing TF-IDF information about tokens.
# It includes the token itself, the document ID where the token is found, and the TF-IDF score.
TFIDFInfo = namedtuple("TFIDFInfo", ("token", "doc_id", "tf_idf"))


class WebpageGeneralInfo:
    """
    A class to store and manage general information about a webpage.
    """

    def __init__(self, title=None, url=None, first_sentence=None):
        self._title = title
        self._url = url
        self._first_sentence = first_sentence

    def get_title(self) -> str:
        """
        Returns the title of the webpage.

        :return: The webpage title.
        """
        return self._title

    def get_url(self) -> str:
        """
        Returns the URL of the webpage.

        :return: The webpage URL.
        """
        return self._url

    def get_first_sentence(self) -> str:
        """
        Returns the first sentence of the webpage content.

        :return: The first sentence of the webpage.
        """
        return self._first_sentence

    def set_title(self, title: str) -> None:
        """
        Sets or updates the title of the webpage.

        :param title: The new title for the webpage.
        :return: None
        """
        self._title = title

    def set_url(self, url: str) -> None:
        """
        Sets or updates the URL of the webpage.

        :param url: The new URL for the webpage.
        :return: None
        """
        self._url = url

    def set_first_sentence(self, first_sentence: str) -> None:
        """
        Sets or updates the first sentence of the webpage content.

        :param first_sentence: The new first sentence of the webpage content.
        :return: None
        """
        self._first_sentence = first_sentence
