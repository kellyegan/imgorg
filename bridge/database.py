import sqlite3
import lancedb
import os

DB_PATH = "data/catalog.sqlite"
VECTOR_PATH = "data/vectors.lancedb"

def get_db():
    # Check if the database exists before attempting to connect
    conn = sqlite3.connect(DB_PATH) if os.path.exists(DB_PATH) else init_db()

    # Returns results as dictionaries
    conn.row_factory = sqlite3.Row

    return conn

def init_db():
    if not os.path.exists("data"):
        os.makedirs("data")
        
    # SQLite Setup
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS images 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    path TEXT UNIQUE, 
                    filename TEXT, 
                    extension TEXT,
                    added_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

    # LanceDB Setup (Vector DB)
    db = lancedb.connect(VECTOR_PATH)
    # We'll define the table schema in Phase 2
    return db

def add_image(path):
    conn = get_db()
    filename = os.path.basename(path)
    extension = os.path.splitext(filename)[1].lower()

    try:
        conn.execute("INSERT INTO images (path, filename, extension) VALUES (?, ?, ?)", (path, filename, extension))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

