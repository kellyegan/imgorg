import os
from PIL import Image

THUMBNAIL_DIR = "data/thumbnails"
THUMBNAIL_SIZE = (512, 512)

def get_thumb_path(id):
    return os.path.join(THUMBNAIL_DIR, f"thumb-{id:08}.webp")

def ensure_thumbnail(id, image_path):
    """Generate a thumbnail and return its path."""
    if not os.path.exists(THUMBNAIL_DIR):
        os.makedirs(THUMBNAIL_DIR)

    thumb_path = get_thumb_path(id)

    if not os.path.exists(thumb_path):
        try:
            with Image.open(image_path) as img:
                img = ensure_rgb(img)
                img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                img.save(thumb_path, format="webp", quality=25, method=6)
        except Exception as e:
            print(f"Failed to make thumbnail for {image_path}: {e}")
            return None

    return thumb_path

def ensure_rgb(img):
    """
    Convert image to RGB when needed.
    """

    if img.mode in ("RGBA", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.getchannel("A"))
        return background

    if img.mode != "RGB":
        return img.convert("RGB")

    return img