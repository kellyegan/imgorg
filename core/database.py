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
    conn.executescript('''CREATE TABLE IF NOT EXISTS images (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        path TEXT UNIQUE, 
                        filename TEXT, 
                        extension TEXT,
                        added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        created_at TEXT,
                        modified_at TEXT,
                        filesize INTEGER,
                        width INTEGER,
                        height INTEGER,
                        filetype TEXT,
                        filehash TEXT
                    );
                                       
                    CREATE TABLE IF NOT EXISTS collections (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL
                    );
                
                    CREATE TABLE IF NOT EXISTS collection_images (
                        collection_id INTEGER,
                        image_id INTEGER,
                        FOREIGN KEY(collection_id) REFERENCES collections(id),
                        FOREIGN KEY(image_id) REFERENCES images(id),
                        PRIMARY KEY (collection_id, image_id)
                    );
                 ''')

    conn.commit()
    conn.close()

    return conn

def init_lancedb():
    # LanceDB Setup (Vector DB)
    db = lancedb.connect(VECTOR_PATH)
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

def add_image_list(img_details_list):
    with get_db() as conn:
        for img_details in img_details_list:
            add_image(img_details, conn)

def update_image(id, **kwargs):
    query = "UPDATE images SET "
    query += "".join([f"{key} = ?, " for key in kwargs.keys()])
    query = query[:-2] + " WHERE id = ?" # Remove the last comma from the query

    query_db(query, list(kwargs.values()) + [id])

def delete_images(ids_to_delete: list[int], conn=None):
    query = "DELETE FROM images WHERE id IN "
    query += f"({("?, " * len(ids_to_delete))[:-2]})"

    query_db(query, ids_to_delete, on_results=None, conn=conn)

def get_all_images():
    query = "SELECT * FROM images ORDER BY filename"

    def on_response(response):
        return [dict(row) for row in response.fetchall()]

    return query_db(query, on_results=on_response)
    
def is_duplicate(filehash, conn=None):
    query = "SELECT * FROM images WHERE filehash = ?"

    def on_response(response):
        return response.fetchone()
    
    return query_db(query, parameters=(filehash,), on_results=on_response, conn=conn)
    
def find_in_catalog(images_by_hash):
    not_in_catalog = []
    duplicate = []
    in_catalog = []

    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        for hash_group in images_by_hash:
            existing_image = is_duplicate(hash_group['hash'], conn)

            if existing_image:
                
                image_list = []

                for image in hash_group["image_list"]:
                    # Check if the same exact image is already in catalog
                    if image["path"] != existing_image["path"]:
                        image_list.append(image)
                    else:
                        in_catalog.append(image)

                if len(image_list) > 0:
                    duplicate.append({"id": existing_image["id"], "image_list": [existing_image, *image_list]})
            else:
               not_in_catalog.append(hash_group)

        return not_in_catalog, duplicate, in_catalog
    
def create_collection(name: str, conn=None):
    query = "INSERT INTO collections (name) VALUES (?)"
    query_db(query, parameters=(name,), on_results=None, conn=conn)

def add_image_to_collection(image_id: int, collection_id: int, conn=None):
    query = "INSERT OR IGNORE INTO collection_images (collection_id, image_id) VALUES (?, ?)"
    query_db(query, parameters=(collection_id, image_id), on_results=None, conn=conn)
