import sqlite3

def get_connection():
    conn = sqlite3.connect("chat.db")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn