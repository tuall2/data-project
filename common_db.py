import sqlite3


# SQLite database connection setup
def get_db_connection():
    conn = sqlite3.connect("database/heart_disease.db")
    conn.row_factory = sqlite3.Row
    return conn
