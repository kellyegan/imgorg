from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp

from kivy.properties import ListProperty

from catalog.db import get_all_images, add_image_list, find_catalog_duplicates  # You must have this function in catalog/db.py
from catalog.image_importer import scan_list_for_images, find_duplicates

class ImportScreen(Screen):
    images_to_import = ListProperty([])

    def set_paths_to_import(self, paths):
        images = scan_list_for_images(paths)
        unique, duplicates = find_duplicates(images)
        not_in_catalog, duplicates_in_catalog = find_catalog_duplicates(unique)

        self.images_to_import = not_in_catalog

        self.list_duplicates(duplicates)
        self.list_catalog_duplicates(duplicates_in_catalog)

    def process_imports(self):
        pass

    def list_duplicates(self, duplicates):
        for duplicate in duplicates:
            print("Duplicates:")
            for image in duplicates[duplicate]:
                print(f"\t{image["path"]}")

    def list_catalog_duplicates(self, duplicates):
        for duplicate in duplicates:
            print(f"\tIn catalog: {duplicate[0]['path']}")
            print(f"\tDuplicate: {duplicate[1]['path']}")

