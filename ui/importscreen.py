from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp

import os

from kivy.properties import ListProperty, StringProperty

from catalog.db import add_image_list, update_image, find_in_catalog  # You must have this function in catalog/db.py
from core.image_importer import find_images, group_by_hash


class StatusLabel(Label):
    pass


class FileToggle(ToggleButton):
    path = StringProperty("")
    hash = StringProperty("group")


class ImageChooser(BoxLayout):
    image_list = ListProperty()
    group = StringProperty("")
    toggle_list = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(image_list=self._on_update_image_list)
        self.update_image_list(self.image_list)

    def _on_update_image_list(self, instance, value):
        self.update_image_list(value)

    def update_image_list(self, image_list):
        toggles = self.ids.image_list
        toggles.clear_widgets()
        self.toggle_list = []

        for image in image_list:
            toggle = FileToggle(path=image["path"], hash=self.group)
            self.toggle_list.append(toggle)
            toggles.add_widget(toggle)

        self.ids.image_thumb.source = self.get_thumbnail()

    def get_thumbnail(self):
        if len(self.image_list) <= 0:
            return ""
        if not os.path.exists(self.image_list[0]["path"]):
            return ""
        return self.image_list[0]["path"]
    
    def get_state(self):
        for index, toggle in enumerate(self.toggle_list):
            if toggle.state == "down":
                return (self.group, self.image_list[index])
        return None


class DuplicatesList(GridLayout):
    title = StringProperty("Duplicates")
    duplicates_list = ListProperty([])
    image_choosers = []

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
            self.image_choosers.append(image_chooser)
            list_widget.add_widget(image_chooser)

    def get_state(self):
        return [chooser.get_state() for chooser in self.image_choosers]

class ImportScreen(Screen):
    images_to_import = ListProperty([])
    duplicate_imports = ListProperty([])
    catalog_duplicates = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(images_to_import=self._on_update_images_to_import)
        self.bind(duplicate_imports=self._on_update_duplicate_imports)
        self.bind(catalog_duplicates=self._on_update_catalog_duplicates)

        self.import_duplicates_list = None
        self.catalog_duplicates_list = None
        self.already_imported_count = 0

    def on_pre_enter(self, *args):
        lists = self.ids.lists
        lists.clear_widgets()

        import_message = "No images to import."
        import_count = len(self.images_to_import)

        if import_count > 0:
            import_message = f"{import_count} image{'s' if import_count > 1 else ''} ready to import."

        if self.already_imported_count > 0:
            import_message += f" {self.already_imported_count} are already in the catalog."

        import_message_label = StatusLabel(text=import_message)
        lists.add_widget(import_message_label)

        if len(self.duplicate_imports) > 0:
            self.import_duplicates_list = DuplicatesList(
                title="These are duplicates. Which do you want to import?",
                duplicates_list=self.duplicate_imports
            )
            lists.add_widget(self.import_duplicates_list)


        if len(self.catalog_duplicates) > 0:
            self.catalog_duplicates_list = DuplicatesList(
                title="These images are duplicates of images in the catalog. Do you want to update the path?",
                duplicates_list=self.catalog_duplicates
            )
            lists.add_widget(self.catalog_duplicates_list)

    def process_import_paths(self, paths):
        print(f"Importing {len(paths)} paths")

        # Search a list of paths for image files
        images = find_images(paths)

        # Group images that appear to be duplicates
        images_by_hash = group_by_hash(images)

        # Check catalog for images already imported
        not_in_catalog, catalog_duplicate, in_catalog = find_in_catalog(images_by_hash)

        unique = [hash["image_list"][0] for hash in not_in_catalog if len(hash["image_list"]) == 1]
        duplicate_imports = [hash for hash in not_in_catalog if len(hash["image_list"]) > 1]

        self.images_to_import = unique
        self.duplicate_imports = [{"group": d["hash"], "image_list": d["image_list"]} for d in duplicate_imports]
        self.catalog_duplicates = [{"group": str(d["id"]), "image_list": d["image_list"]} for d in catalog_duplicate]
        self.already_imported_count = len(in_catalog)

    def exit_import(self):
        self.images_to_import = []
        self.duplicate_imports = []
        self.catalog_duplicates = []

        app = App.get_running_app()
        app.view_thumbnail_browser()

    def import_images(self):
        selections = []
        if self.import_duplicates_list:
            selections = [choice[1] for choice in self.import_duplicates_list.get_state()]

        # Update database with any selected new paths for existing images
        if self.catalog_duplicates_list:
            updates = self.catalog_duplicates_list.get_state()
            for update in updates:
                if update:
                    id = update[0]
                    image_details = update[1]

                    print(image_details)
                    if "id" not in image_details.keys():
                        update_image(id, **image_details)

        # Import new images to database
        add_image_list(self.images_to_import + selections)

        app = App.get_running_app()
        app.update_image_list()
        self.exit_import()

    def _on_update_images_to_import(self, instance, value):
        pass

    def _on_update_duplicate_imports(self, instance, value):
        pass

    def _on_update_catalog_duplicates(self, instance, value):
        pass