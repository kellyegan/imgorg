import os
from datetime import datetime
from pathlib import Path
from PIL import Image
import hashlib

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}

def get_md5_hash(file_path, chunk_size=8192):
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"Error hashing {file_path}: {e}")
        return None
    
def get_image_details(file_path):
    results = {
        'filesize': None,
        'created_at': None,
        'modified_at': None,
        'width': None,
        'height': None,
        'filetype': None,
        'filehash': None,
    }
    try:
        # Get file size in bytes
        stat = os.stat(file_path)
        results['filesize'] = stat.st_size
        results['created_at'] = datetime.fromtimestamp(stat.st_ctime).isoformat()
        results['modified_at'] = datetime.fromtimestamp(stat.st_mtime).isoformat()

        # Get image dimensions
        with Image.open(file_path) as img:
            width, height = img.size
            results['width'] = width
            results['height'] = height
            results['filetype'] = img.format

        results['filehash'] = get_md5_hash(file_path)
    except Exception as e:
        print(f"Error reading image details for {file_path}: {e}")
        return None
    
    return results
    
def scan_for_images(path):
    if os.path.isdir(path):
        return scan_dir_for_images(path)
    elif os.path.isfile(path):
        details = get_image_details(path)
        if details:
            return [details]
    return []

def scan_dir_for_images(base_dir):
    base_path = Path(base_dir)
    images = []
    
    for filepath in base_path.rglob("*"):
        if filepath.suffix.lower() in IMAGE_EXTENSIONS and filepath.is_file():
            image_details = get_image_details(filepath)
            if image_details:
                images.append(image_details)
           
    return images
