from contextlib import contextmanager
from psycopg2 import pool
from secret import DB_NAME, USER, PASSWORD, HOST, PORT


def CreateConnectionPool():
    conn_pool = pool.SimpleConnectionPool(1, 20,
                                          dbname=DB_NAME,
                                          user=USER,
                                          password=PASSWORD,
                                          host=HOST,
                                          port=PORT)
    return conn_pool


@contextmanager
def GetConCur(conn_pool: pool.SimpleConnectionPool):
    conn = conn_pool.getconn()
    cursor = conn.cursor()
    try:
        yield conn, cursor
    finally:
        cursor.close()
        conn_pool.putconn(conn)
