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

def query_db(query: str, values : tuple=(), on_results=None, conn=None):
    if conn is None:
        print('No database connection provided. Creating a new one.')
        with get_connection(DB_NAME) as conn:
            return query_db(query, values, on_results, conn=conn)
    else:
        print('Using provided database connection.')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        response = cur.execute(query, values)
        conn.commit()
        print(on_results == None)
        return on_results(response)

def get_all_images():
    query = "SELECT * FROM images ORDER BY filename"

    def on_response(response):
        return [dict(row) for row in response.fetchall()]

    return query_db(query, on_results=on_response)
    
def is_duplicate(filehash, conn=None):
    query = "SELECT * FROM images WHERE filehash = ?"

    def on_response(response):
        return response.fetchone()
    
    return query_db(query, values=(filehash,), on_results=on_response, conn=conn)
    
def find_in_catalog(images_by_hash):
    not_in_catalog = []
    duplicate = []
    in_catalog = []

    with get_connection(DB_NAME) as conn:
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

def add_image(connection, img_details, ignore_duplicate = False):
    cur = connection.cursor()

    # Skip adding duplicate image paths
    cur.execute("SELECT * FROM images WHERE path = ?", (img_details['path'],))
    if cur.fetchone():
        print("This is a duplicate image path. Skipping")
        return  # Silently skip this image

    try:
        cur.execute("""
            INSERT OR IGNORE INTO images (path, filename, created_at, modified_at, filesize, width, height, filetype, filehash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (img_details['path'], img_details['filename'], img_details['created_at'], img_details['modified_at'],
            img_details['filesize'], img_details['width'], img_details['height'], img_details['filetype'], img_details['filehash']))
    except Exception as e:
        print(f"Error processing {img_details['path']}: {e}")

    connection.commit()

def update_image(id, **kwargs):
    with get_connection(DB_NAME) as conn:
        values = list(kwargs.values())
        values.append(id)
        values = tuple(values)

        query = "UPDATE images SET "
        query += "".join([f"{key} = ?, " for key in kwargs.keys()])
        query = query[:-2] + " WHERE id = ?" # Remove the last comma from the query
        
        cur = conn.cursor()
        cur.execute(query, values)

        conn.commit()

def delete_images(ids_to_delete, **kwargs):
    with get_connection(DB_NAME) as conn:
        query = "DELETE FROM images WHERE id IN "
        query += f"({("?, " * len(ids_to_delete))[:-2]})"
        print(query)
        print(ids_to_delete)
        cur = conn.cursor()
        cur.execute(query, tuple(ids_to_delete))

        conn.commit()


def add_image_list(img_details_list):
    with get_connection(DB_NAME) as conn:
        for img_details in img_details_list:
            add_image(conn, img_details)