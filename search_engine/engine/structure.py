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


# class DocNode:
#     def __init__(self, doc_ids=None, url=None, tf_idf=None):
#         self._doc_ids = doc_ids
#         self._url = url
#         self._tf_idf = tf_idf
#         self.next = None
#
#     def get_doc_ids(self):
#         return self._doc_ids
#
#     def get_url(self):
#         return self._doc_ids
#
#     def get_tf_idf(self):
#         return self._tf_idf
#
#     def set_doc_ids(self, _doc_ids):
#         self._doc_ids = _doc_ids
#
#     def set_url(self, url):
#         self._url = url
#
#     def set_tf_idf(self, tf_idf):
#         self._tf_idf = tf_idf
#
#
# class DocLinkedList:
#     def __init__(self):
#         self.head = None
#
#     def insert_sorted(self, new_node: DocNode):
#         if not self.head or self.head.get_tf_idf() < new_node.get_tf_idf():
#             new_node.next = self.head
#             self.head = new_node
#         else:
#             current = self.head
#             while current.next and current.next.get_tf_idf() >= new_node.get_tf_idf():
#                 current = current.next
#             new_node.next = current.next
#             current.next = new_node
#
#
# class TokenStructure:
#     def __init__(self, token, doc: DocLinkedList = None, doc_num=None, total_num=None):
#         self._token = token
#         self._doc = doc
#         self._doc_num = doc_num
#         self._total_num = total_num
#
#     def get_token(self):
#         return self._token
#
#     def get_doc_num(self):
#         return self._doc_num
#
#     def get_doc(self):
#         return self._doc
#
#     def get_total_num(self):
#         return self._total_num
#
#     def set_doc_num(self, doc_num):
#         self._doc_num = doc_num
#
#     def set_total_num(self, total_num):
#         self._total_num = total_num
#
#     def set_doc(self, doc: DocLinkedList):
#         self._doc = doc
#
#     """后续添加对于doc链表的操作，应该会增加或者减少链表中的内容"""
