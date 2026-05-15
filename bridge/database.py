import sqlite3
import lancedb
import os

DB_PATH = "data/catalog.sqlite"
VECTOR_PATH = "data/vectors.lancedb"

def init_db():
    if not os.path.exists("data"):
        os.makedirs("data")
        
    # SQLite Setup
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS images 
                   (id INTEGER PRIMARY KEY, path TEXT, hash TEXT, added_at DATETIME)''')
    conn.close()

    # LanceDB Setup (Vector DB)
    db = lancedb.connect(VECTOR_PATH)
    # We'll define the table schema in Phase 2
    return db
