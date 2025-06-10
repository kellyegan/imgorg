from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp

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
        self.bind(image_list=self._update_image_list)

    def _update_image_list(self, instance, value):
        self.ids.image_list.clear_widgets()
        for item in value:
            toggle = FileToggle(path=item["path"], hash=self.hash)
            self.ids.image_list.add_widget(toggle)

class DuplicatesList(GridLayout):
    pass

class ImportScreen(Screen):
    images_to_import = ListProperty([])
    duplicate_imports = ListProperty([])
    catalog_duplicates = ListProperty([])

    def set_paths_to_import(self, paths):
        images = scan_list_for_images(paths)
        unique, duplicates = find_duplicates(images)
        not_in_catalog, duplicates_in_catalog = find_catalog_duplicates(unique)

        self.images_to_import = not_in_catalog
        self.duplicate_imports = duplicates
        self.catalog_duplicates = duplicates_in_catalog

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
