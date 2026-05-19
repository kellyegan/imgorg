import os
from PIL import Image

THUMBNAIL_DIR = "data/thumbnails"
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
                img = ensure_rgb(img)
                img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

                kwargs = {}

                img.save(thumb_path, format="webp")
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