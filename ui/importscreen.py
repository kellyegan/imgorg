from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock

from kivy.properties import ListProperty

from catalog.db import get_all_images, add_image_list, find_catalog_duplicates  # You must have this function in catalog/db.py
from catalog.image_importer import scan_for_images, find_duplicates

class ImportScreen(Screen):
    images_to_import = ListProperty([])

    def set_paths_to_import(self, paths):
        images = []
        for path in paths:
            images += scan_for_images(path)

        self.images_to_import = images
        unique, duplicates = find_duplicates(self.images_to_import)

        print(f"{len(unique)} unique images in imports")
        for duplicate in duplicates:
            print("These images appear to be the same:")
            for duplicate_image in duplicates[duplicate]:
                print(duplicate_image["path"])

        not_in_catalog, duplicate_in_catalog, in_catalog_count = find_catalog_duplicates(unique)

        print(f"{len(not_in_catalog)} imports not in catalog. {in_catalog_count} already in catalog.")
        print(f"{len(duplicate_in_catalog)} imports suspected duplicates.")

        for duplicate in duplicate_in_catalog:
            print("Duplicates:")
            print(f"{duplicate[0]['filename']} matches {duplicate[1]['filename']}")

    def list_duplicates():
        pass

