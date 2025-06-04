from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock

from kivy.properties import ListProperty

from catalog.db import get_all_images, add_image_list, check_catalog_duplicate  # You must have this function in catalog/db.py
from catalog.image_importer import scan_for_images, find_duplicates

class ImportScreen(Screen):
    images_to_import = ListProperty([])

    def set_paths_to_import(self, paths):
        images = []
        for path in paths:
            images += scan_for_images(path)

        self.images_to_import = images
        unique, duplicates = find_duplicates(self.images_to_import)
        self.unique_images = unique
        self.duplicates = duplicates

        print(f"{len(self.unique_images)} unique images")
        for duplicate in self.duplicates:
            print("Duplicates:")
            for duplicate_image in self.duplicates[duplicate]:
                print(duplicate_image["path"])



    # unique, duplicates = find_duplicates(images)

    # print(f"Unique images: {len(unique)}")

    # for duplicate_group in duplicates.values():
    #     print("Duplicates:")
    #     for image in duplicate_group:
    #         print(image["path"])