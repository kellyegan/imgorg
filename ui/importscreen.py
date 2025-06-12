from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp

import os

from kivy.properties import ListProperty, StringProperty

from catalog.db import get_all_images, add_image_list, find_catalog_duplicates  # You must have this function in catalog/db.py
from catalog.image_importer import scan_list_for_images, find_duplicates

class FileToggle(ToggleButton):
    path = StringProperty("")
    hash = StringProperty("group")

class ImageChooser(BoxLayout):
    image_list = ListProperty()
    hash = StringProperty("A")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(image_list=self._on_update_image_list)
        self.update_image_list(self.image_list)

    def _on_update_image_list(self, instance, value):
        self.update_image_list(value)

    def update_image_list(self, image_list):
        self.ids.image_list.clear_widgets()
        for image in image_list:
            toggle = FileToggle(path=image["path"], hash=self.hash)
            self.ids.image_list.add_widget(toggle)
        self.ids.image_thumb.source = self.get_thumbnail()

    def get_thumbnail(self):
        if len(self.image_list) <= 0:
            return ""
        if not os.path.exists(self.image_list[0]["path"]):
            return ""
        return self.image_list[0]["path"]

class DuplicatesList(GridLayout):
    title = StringProperty("Duplicates")
    duplicates_list = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(duplicates_list=self._on_update_duplicate_list)

    def _on_update_duplicate_list(self, instance, value):
        self.ids.duplicates_list.clear_widgets()

        for item in value:
            image_chooser = ImageChooser(hash=item["hash"], image_list=item["image_list"])
            self.ids.duplicates_list.add_widget(image_chooser)

class ImportScreen(Screen):
    images_to_import = ListProperty([])
    duplicate_imports = ListProperty([])
    catalog_duplicates = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(images_to_import=self._on_update_images_to_import)
        self.bind(duplicate_imports=self._on_update_duplicate_imports)
        self.bind(catalog_duplicates=self._on_update_catalog_duplicates)
        self.duplicate_imports = [
            { 
                "hash": "group-1",  
                "image_list": [
                    {"path":"/Users/kpe/Desktop/Level_0/8663892916_f048be298f_o.jpg"},
                    {"path":"/Users/kpe/Desktop/Level_0/14305059168_6f889b3b49_o.jpg"},
                    {"path":"/Users/kpe/Desktop/Level_0/39737483343_97c4be7232_o.jpg"}
                ]
            }, 
            {
                "hash": "group-1",
                "image_list": [
                    {"path":"/Users/kpe/Desktop/Level_0/45065073822_5273e26d5e_o.jpg"},
                    {"path":"/Users/kpe/Desktop/Level_0/14305059168_6f889b3b49_o.jpg"},
                ]
            }
        ]

        self.catalog_duplicates = [
            {
                "hash": "group-1",
                "image_list": [
                    {"path":"/Users/kpe/Desktop/Level_0/22505248287_c658ab9b55_o.jpg"},
                    {"path":"/Users/kpe/Desktop/Level_0/14305059168_6f889b3b49_o.jpg"}
                ]
            }
        ]

    def set_paths_to_import(self, paths):
        images = scan_list_for_images(paths)
        unique, duplicates = find_duplicates(images)
        not_in_catalog, duplicates_in_catalog = find_catalog_duplicates(unique)

        self.images_to_import = not_in_catalog

    def _on_update_images_to_import(self, instance, value):
        pass

    def _on_update_duplicate_imports(self, instance, value):
        pass

    def _on_update_catalog_duplicates(self, instance, value):
        pass