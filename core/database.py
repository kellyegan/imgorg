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
    conn.execute('''CREATE TABLE IF NOT EXISTS images (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        path TEXT UNIQUE, 
                        filename TEXT, 
                        extension TEXT,
                        added_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        created_at TEXT,
                        modified_at TEXT,
                        filesize INTEGER,
                        width INTEGER,
                        height INTEGER,
                        filetype TEXT,
                        filehash TEXT
                    );
                 ''')
    conn.commit()
    conn.close()

    # LanceDB Setup (Vector DB)
    db = lancedb.connect(VECTOR_PATH)
    # We'll define the table schema in Phase 2
    return db

def query_db(query: str, parameters : tuple=(), on_results=None, conn=None):
    # If no database connection provided, create one
    if conn is None:
        with get_db() as conn:
            return query_db(query, parameters, on_results, conn=conn)
    else:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        response = cur.execute(query, parameters)
        conn.commit()
        if on_results:
            return on_results(response)

def add_image(img_details, conn=None):
    # Skip adding duplicate image paths
    query = "SELECT * FROM images WHERE path = ?"
    if query_db(query, (img_details['path'],), on_results=lambda r: r.fetchone(), conn=conn):
        return

    try:
        query = """
            INSERT OR IGNORE INTO images (path, filename, created_at, modified_at, filesize, width, height, filetype, filehash)
            VALUES (:path, :filename, :created_at, :modified_at, :filesize, :width, :height, :filetype, :filehash)
        """   
        query_db(query, img_details, on_results=None, conn=conn)
    except Exception as e:
        print(f"Error processing {img_details['path']}: {e}")

    conn.commit()
