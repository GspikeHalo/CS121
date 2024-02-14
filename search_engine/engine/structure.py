class TokenStructure:
    def __init__(self, token, doc=None, doc_num=None, total_num=None):
        self._token = token
        self._doc = doc
        self._doc_num = doc_num
        self._total_num = total_num

    def get_token(self):
        return self._token

    def get_doc_ids(self):
        return self._doc_ids

    def get_doc_num(self):
        return self._doc_num

    def get_total_num(self):
        return self._total_num

    def set_doc_ids(self, doc_ids):
        self._doc_ids = doc_ids

    def set_doc_num(self, doc_num):
        self._doc_num = doc_num

    def set_total_num(self, total_num):
        self._total_num = total_num


class DocStructure:
    def __init__(self, doc_ids=None, url=None, tf_idf=None):
        self._doc_ids = doc_ids
        self._url = url
        self._tf_idf = tf_idf
        self.next = None

    def get_doc_ids(self):
        return self._doc_ids

    def get_url(self):
        return self._doc_ids

    def get_tf_idf(self):
        return self._tf_idf

    def set_doc_ids(self, _doc_ids):
        self._doc_ids = _doc_ids

    def set_url(self, url):
        self._url = url

    def set_tf_idf(self, tf_idf):
        self._tf_idf = tf_idf


class DocLinkedList:
    def __init__(self):
        self.head = None

    def insert_sorted(self, new_node):
        if not self.head or self.head.get_tf_idf() < new_node.get_tf_idf():
            new_node.next = self.head
            self.head = new_node
        else:
            current = self.head
            while current.next and current.next.get_tf_idf() >= new_node.get_tf_idf():
                current = current.next
            new_node.next = current.next
            current.next = new_node
