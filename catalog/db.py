# catalog/db.py
import sqlite3
import os

DB_NAME = 'catalog.db'

def get_connection(database_name):
    if not os.path.exists(database_name):
        return create_database(database_name)

    return sqlite3.connect(database_name)

def create_database(database_name):
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE,
            filename TEXT,
            created_at TEXT,
            modified_at TEXT,
            filesize INTEGER,
            width INTEGER,
            height INTEGER,
            filetype TEXT,
            filehash TEXT
        );
    """)
    conn.commit()
    return conn

def get_all_images():
    with get_connection(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM images ORDER BY filename")
        rows = cur.fetchall()
        return [dict(row) for row in rows]
