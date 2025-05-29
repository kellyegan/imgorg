from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

from kivy.core.window import Window
from kivy.metrics import dp

from catalog.db import get_all_images, add_image_list, check_catalog_duplicate  # You must have this function in catalog/db.py
from ui.widgets import ImageCard       # This needs to be defined as in Step 3
from catalog.image_importer import scan_for_images


# Load the Kivy layout for MainScreen
Builder.load_file('ui/main_screen.kv')


class MainScreen(Screen):
    cols = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(size=self.update_cols)
        self.update_cols()

    def update_cols(self, *args):
        # Thumbnail width + spacing
        thumb_width = dp(200)
        spacing = dp(10)  # padding + spacing between items
        available_width = Window.width - spacing
        new_cols = max(1, int(available_width // thumb_width))
        self.cols = new_cols

        # Update the grid layout if it exists
        if hasattr(self.ids, "image_grid"):
            self.ids.image_grid.cols = self.cols

    def on_pre_enter(self):
        self.ids.image_grid.clear_widgets()
        images = get_all_images()

        if len(images) <= 0:
            self.ids.no_images_label.opacity = 1
            self.ids.no_images_label.height = 100
            self.ids.scroll_area.opacity = 0
            self.ids.scroll_area.height = 0
            self.ids.scroll_area.size_hint_y = None
            return
        else:
            self.ids.no_images_label.opacity = 0
            self.ids.no_images_label.height = 0
            self.ids.no_images_label.size_hint_y = None
            self.ids.scroll_area.opacity = 1
            self.ids.scroll_area.height = 100
            self.ids.scroll_area.size_hint_y = 1

        for img in images:
            card = ImageCard(img)
            self.ids.image_grid.add_widget(card)


class ImageCatalogApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen(name='main'))
        Window.bind(on_drop_file=self._on_drop_file)
        return self.sm
    
    def _on_drop_file(self, window, filepath, x, y):
        path_string = filepath.decode('utf-8')
        images, import_duplicates = scan_for_images(path_string)
        imports, catalog_duplicates = check_catalog_duplicate(images)

        add_image_list(imports)
        
        if 'main' in self.sm.screen_names:
            self.sm.get_screen('main').on_pre_enter()


if __name__ == '__main__':
    ImageCatalogApp().run()
