import os
from datetime import datetime
from pathlib import Path
from PIL import Image
import hashlib

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}


def calculate_file_hash(file_path, chunk_size=8192):
    hasher = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error hashing {file_path}: {e}")
        return None


def get_image_details(file_path):
    results = {
        'filename': None,
        'path': None,
        'filesize': None,
        'created_at': None,
        'modified_at': None,
        'width': None,
        'height': None,
        'filetype': None,
        'filehash': None,
    }
    try:
        path = Path(file_path)
        results['filename'] = path.name
        results['path'] = str(path.absolute())

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

        results['filehash'] = calculate_file_hash(file_path)
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
            return [details] , []
    return [], []


def scan_dir_for_images(base_dir):
    base_path = Path(base_dir)
    images = []
    duplicates = []
    hashes = set()
    
    for filepath in sorted(base_path.rglob("*"), key=lambda x: (len(str(x)), str(x).lower())):
        if filepath.suffix.lower() in IMAGE_EXTENSIONS and filepath.is_file():
            image_details = get_image_details(filepath)
            if image_details:
                if image_details['filehash'] not in hashes:
                    hashes.add(image_details['filehash'])
                    images.append(image_details)
                else:
                    duplicates.append(image_details)
           
    return images, duplicates
