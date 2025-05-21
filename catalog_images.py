import os
import sqlite3
from datetime import datetime
from pathlib import Path
from PIL import Image
from tqdm import tqdm
import hashlib

# Supported image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}

# Database setup
DB_PATH = 'image_metadata.db'

def init_db(conn):
    c = conn.cursor()
    c.execute("""
        CREATE TABLE images (
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

def get_md5(file_path, chunk_size=8192):
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"Error hashing {file_path}: {e}")
        return None

def get_image_info(file_path):
    try:
        # Get file size in bytes
        stat = os.stat(file_path)
        filesize = stat.st_size

        # Get image dimensions
        with Image.open(file_path) as img:
            width, height = img.size
            filetype = img.format

        filehash = get_md5(file_path)

        return filesize, width, height, filetype, filehash
    except Exception as e:
        print(f"Error reading image info for {file_path}: {e}")
        return None, None, None, None, None

def scan_images(base_dir, conn):
    base_path = Path(base_dir)
    c = conn.cursor()
    
    for file_path in tqdm(base_path.rglob("*")):
        if file_path.suffix.lower() in IMAGE_EXTENSIONS and file_path.is_file():
            rel_path = str(file_path.relative_to(base_path))
            stat = file_path.stat()
            created_at = datetime.fromtimestamp(stat.st_ctime).isoformat()
            modified_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
            filesize, width, height, filetype, filehash = get_image_info(file_path)
            
            try:
                c.execute("""
                    INSERT OR IGNORE INTO images (path, filename, created_at, modified_at, filesize, width, height, filetype, filehash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (rel_path, file_path.name, created_at, modified_at, filesize, width, height, filetype, filehash))
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    conn.commit()



def main():
    base_dir = input("Enter path to your image directory: ").strip()
    if not os.path.isdir(base_dir):
        print("Invalid directory.")
        return

    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    scan_images(base_dir, conn)
    print("✅ Done indexing images.")

if __name__ == "__main__":
    main()
