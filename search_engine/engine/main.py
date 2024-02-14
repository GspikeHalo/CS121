#  .search_engine/engine/main.py


from .method import Method
from .databaseprocessor import DatabaseProcessor
from .error import *


class Engine:
    def __init__(self):
        self.method = Method()
        self.db = DatabaseProcessor()

    def main(self):
        pass