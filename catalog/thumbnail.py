import os
from PIL import Image

THUMBNAIL_DIR = ".thumbnails"
THUMBNAIL_SIZE = (200, 200)

def ensure_thumbnail(image_path):
    """Generate a thumbnail and return its path."""
    if not os.path.exists(THUMBNAIL_DIR):
        os.makedirs(THUMBNAIL_DIR)

    filename = os.path.basename(image_path)
    name, ext = os.path.splitext(filename)
    thumb_path = os.path.join(THUMBNAIL_DIR, f"{name}_thumb.webp")

    if not os.path.exists(thumb_path):
        try:
            with Image.open(image_path) as img:
                img = img.convert('RGB')
                img.thumbnail(THUMBNAIL_SIZE)
                img.convert('RGB').save(thumb_path, "webp")
        except Exception as e:
            print(f"Failed to make thumbnail for {image_path}: {e}")
            return None

    return thumb_path
