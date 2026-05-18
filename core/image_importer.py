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

def find_images(path_list: list[str]):
    """
    Look through a list of paths for image files
    """
    images = set()

    for path_string in path_list:
        path = Path(path_string)

        if not path:
            print(f"ERROR: {path_string} is not a valid path.")
            continue
        
        if path.is_dir():
            for filepath in sorted(path.rglob("*"), key=lambda x: (len(str(x)), str(x).lower())):
                if filepath.is_file() and filepath.suffix.lower() in IMAGE_EXTENSIONS:
                    images.add(filepath.as_posix())
        elif path.is_file():
            images.add(path.as_posix())

    image_details = [get_image_details(image) for image in list(images)]
    return image_details

def group_by_hash(images):
    images_by_hash = dict()

    for image_a in images:
        hash_a = image_a['filehash']

        same_path = False
        if hash_a in images_by_hash:
            for image_b in images_by_hash[hash_a]:
                if image_a["path"] == image_b["path"]:
                    same_path = True
            if not same_path:
                images_by_hash[hash_a].append(image_a)
        else:
            images_by_hash[hash_a] = [image_a]

    images_by_hash = [{"hash": hash, "image_list": image_list} for hash, image_list in images_by_hash.items()]
    # unique = [image_list[0] for hash, image_list in images_by_hash.items() if len(image_list) == 1]

    return images_by_hash

