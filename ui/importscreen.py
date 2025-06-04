from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock

from kivy.properties import ListProperty

from catalog.db import get_all_images, add_image_list, check_catalog_duplicate  # You must have this function in catalog/db.py
from catalog.image_importer import scan_for_images

class ImportScreen(Screen):
    import_queue = ListProperty([])

    def on_enter(self, *args):
        super().on_enter(*args)

        print("The import queue")
        for path in self.import_queue:
            print(path)
        print("That was the import queue")

    def add_to_import_queue(self, image_path):
        self.import_queue.append(image_path)