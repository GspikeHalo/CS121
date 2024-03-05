#  .search_engine/engine/connection_pool.py

import sqlite3
from queue import Queue


class SQLiteConnectionPool:
    """
        A simple SQLite connection pool class that manages a pool of SQLite connections.

    Attributes:
        _pool (Queue): A thread-safe queue that holds the pool of active SQLite connections.
        _database_path (str): The file path to the SQLite database.

    Parameters:
        database_path (str): The path to the SQLite database file. This is where the database is located on disk.
        pool_size (int, optional): The maximum number of connections the pool can hold. Defaults to 5.
        timeout (int, optional): The timeout in seconds for attempts to get a connection from the pool. Defaults to 20.
    """
    def __init__(self, database_path, pool_size=5, timeout=20):
        self._pool = Queue(maxsize=pool_size)
        self._database_path = database_path
        for _ in range(pool_size):
            conn = sqlite3.connect(database_path, check_same_thread=False, timeout=timeout)
            self._pool.put(conn)

    def get_connection(self):
        """
        get a connection from the pool.

        :return: An SQLite connection from the pool.
        """
        return self._pool.get()

    def release_connection(self, conn) -> None:
        """
        Releases a connection back to the pool.

        :param conn: The SQLite connection to be released back into the pool.
        :return: None
        """
        self._pool.put(conn)

    def close_all_connections(self) -> None:
        """
        Closes all connections in the pool.

        :return: None
        """
        while not self._pool.empty():
            conn = self._pool.get()
            conn.close()
