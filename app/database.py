import sqlite3

DATABASE_NAME = "library.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row # rows will be returned as dictionaries
    return conn

