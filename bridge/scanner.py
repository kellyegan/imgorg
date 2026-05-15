# bridge/scanner.py
import os
from .database import add_image

SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}

def scan_directory(root_path: str):
    count = 0
    for root, _, files in os.walk(root_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in SUPPORTED_FORMATS:
                full_path = os.path.join(root, file)
                add_image(full_path)
                count += 1
    return count