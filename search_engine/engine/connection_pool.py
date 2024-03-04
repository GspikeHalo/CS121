import sqlite3
from queue import Queue


class SQLiteConnectionPool:
    def __init__(self, database_path, pool_size=5, timeout=20):
        self.pool = Queue(maxsize=pool_size)
        self.database_path = database_path
        for _ in range(pool_size):
            conn = sqlite3.connect(database_path, check_same_thread=False, timeout=timeout)
            self.pool.put(conn)

    def get_connection(self):
        return self.pool.get()

    def release_connection(self, conn):
        self.pool.put(conn)

    def close_all_connections(self):
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()
