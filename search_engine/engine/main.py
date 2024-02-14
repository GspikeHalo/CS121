#  .search_engine/engine/main.py

from .databaseprocessor import DatabaseProcessor


class Engine:
    def __init__(self):
        self.db = DatabaseProcessor()

    def main(self):
        pass

