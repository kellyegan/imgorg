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
    
def is_duplicate(connection, filehash):
    cur = connection.cursor()
    
    cur.execute("SELECT * FROM images WHERE filehash = ?", (filehash,))
    existing_image = cur.fetchone()

    if existing_image:
        return existing_image
    else:
        return None
    
def find_catalog_duplicates(image_details_list):
    images = []
    duplicates = []

    with get_connection(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        for image_details in image_details_list:
            existing_image = is_duplicate(conn, image_details['filehash'])

            if existing_image:
                print(f"Duplicate found: {existing_image["path"]}")
                # If it is same path just ignore it
                if image_details["path"] != existing_image["path"]:
                    duplicates.append({"id": existing_image["id"], "image_list": [existing_image, image_details]})
            else:
               images.append(image_details)

        return images, duplicates

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

def add_image_list(img_details_list):
    with get_connection(DB_NAME) as conn:
        for img_details in img_details_list:
            add_image(conn, img_details)