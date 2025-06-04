from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import Config

from kivy.properties import ListProperty, NumericProperty

from ui.thumbnailbrowserscreen import ThumbnailBrowserScreen
from ui.imagepreviewscreen import ImagePreviewScreen
from ui.importscreen import ImportScreen

from catalog.db import get_all_images, add_image_list, check_catalog_duplicate  # You must have this function in catalog/db.py
from catalog.image_importer import scan_for_images

Config.set('kivy', 'exit_on_escape', '0')

class ImgOrgApp(App):
    image_list = ListProperty([])
    active_index = NumericProperty(None)
    selected_indexes = ListProperty([])

    def build(self):
        Builder.load_file("ui/thumbnailbrowserscreen.kv")
        Builder.load_file("ui/imagepreviewscreen.kv")
        Builder.load_file("ui/importscreen.kv")

        Window.bind(on_drop_file=self._on_drop_file)
        
        Window.size = (1024, 1024)
        Window.top = 50
        Window.left = 10

        self.sm = ScreenManager()
        self.sm.add_widget(ThumbnailBrowserScreen())
        self.sm.add_widget(ImagePreviewScreen())
        self.sm.add_widget(ImportScreen())

        self.image_list = get_all_images()
        self.active_index = 0

        return self.sm
    
    def view_image_preview(self, index):
        self.set_active(index)
        self.sm.transition.direction = 'up'
        self.sm.current = "preview"

    def view_thumbnail_browser(self):
        self.sm.transition.direction = 'down'
        self.sm.current = "browser"

    def _on_drop_file(self, window, filepath, x, y):
        path_string = filepath.decode('utf-8')
        self.add_images_from_path(path_string)
        self.view_thumbnail_browser()

    def set_active(self, index):
        if index < 0 or index >= len(self.image_list):
            return
        self.active_index = index

    def select_index(self, index):
        if index < 0 or index >= len(self.image_list):
            return
        if index not in self.selected_indexes:
            self.selected_indexes.append(index)

    def deselect_index(self, index):
        if index in self.selected_indexes:
            self.selected_indexes.remove(index)

    def toggle_selection(self, index):
        if index in self.selected_indexes:
            self.deselect_index(index)
        else:
            self.select_index(index)
            
    def selected_all_indexes(self):
        self.selected_indexes = [i for i in range(len(self.image_list))]

    def deselect_all_indexes(self):
        self.selected_indexes = []

    def select_between_active_and_index(self, index):
        start = index if index < self.active_index else self.active_index
        end = index if index > self.active_index else self.active_index

        for i in range(start, end + 1):
            self.select_index(i)

    def add_images_from_path(self, filepath):
        images, import_duplicates = scan_for_images(filepath)
        imports, catalog_duplicates = check_catalog_duplicate(images)
        add_image_list(imports)
        self.image_list = get_all_images()


if __name__ == "__main__":
    ImgOrgApp().run()