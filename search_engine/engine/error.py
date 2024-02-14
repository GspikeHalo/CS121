#  .search_engine/engine/error.py

class DataBaseOpenFail(Exception):
    """Occurs when the database cannot open"""
    def __str__(self):
        return "database open file!"
