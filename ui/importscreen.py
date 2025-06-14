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
from catalog.image_importer import find_images, find_duplicates

class FileToggle(ToggleButton):
    path = StringProperty("")
    hash = StringProperty("group")

class ImageChooser(BoxLayout):
    image_list = ListProperty()
    group = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(image_list=self._on_update_image_list)
        self.update_image_list(self.image_list)

    def _on_update_image_list(self, instance, value):
        self.update_image_list(value)

    def update_image_list(self, image_list):
        self.ids.image_list.clear_widgets()
        for image in image_list:
            toggle = FileToggle(path=image["path"], hash=self.group)
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
        self.update_duplicates_list(self.duplicates_list)

    def on_pre_enter(self):
        self.update_duplicates_list(self.duplicates_list)

    def _on_update_duplicate_list(self, instance, value):
        self.update_duplicates_list(self.duplicates_list)

    def update_duplicates_list(self, list):
        list_widget = self.ids.duplicates_list
        list_widget.clear_widgets()

        for item in list:
            image_chooser = ImageChooser(group=item["group"], image_list=item["image_list"])
            list_widget.add_widget(image_chooser)

class ImportScreen(Screen):
    images_to_import = ListProperty([])
    duplicate_imports = ListProperty([])
    catalog_duplicates = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(images_to_import=self._on_update_images_to_import)
        self.bind(duplicate_imports=self._on_update_duplicate_imports)
        self.bind(catalog_duplicates=self._on_update_catalog_duplicates)

    def on_pre_enter(self, *args):
        lists = self.ids.lists
        lists.clear_widgets()

        if len(self.duplicate_imports) > 0:
            import_duplicates_list = DuplicatesList(
                title="These images selected for import appear to be duplicates",
                duplicates_list=self.duplicate_imports
            )
            lists.add_widget(import_duplicates_list)


        if len(self.catalog_duplicates) > 0:
            catalog_duplicates_list = DuplicatesList(
                title="These images appear to already be in the catalog",
                duplicates_list=self.catalog_duplicates
            )
            lists.add_widget(catalog_duplicates_list)

    def process_import_paths(self, paths):
        print(f"Importing {len(paths)} paths")

        # Search a list of paths for image files
        images = find_images(paths)

        # Look for any duplicates with images
        unique, duplicates = find_duplicates(images)
        self.duplicate_imports = [{"group": d["hash"], "image_list": d["image_list"]} for d in duplicates]

        # Check catalog for images that might also be duplicates
        not_in_catalog, duplicates_in_catalog = find_catalog_duplicates(unique)
        self.images_to_import = not_in_catalog
        self.catalog_duplicates = [{"group": str(d["id"]), "image_list": d["image_list"]} for d in duplicates_in_catalog]

    def cancel_import(self):
        self.images_to_import = []
        self.duplicate_imports = []
        self.catalog_duplicates = []

        app = App.get_running_app()
        app.view_thumbnail_browser()

    def import_images(self):
        add_image_list(self.images_to_import)
        app = App.get_running_app()
        app.update_image_list()

        self.cancel_import()


    def _on_update_images_to_import(self, instance, value):
        pass

    def _on_update_duplicate_imports(self, instance, value):
        pass

    def _on_update_catalog_duplicates(self, instance, value):
        pass