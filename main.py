from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

from kivy.core.window import Window

from catalog.db import get_all_images  # You must have this function in catalog/db.py
from ui.widgets import ImageCard       # This needs to be defined as in Step 3

# Load the Kivy layout for MainScreen
Builder.load_file('ui/main_screen.kv')


class MainScreen(Screen):
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
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        Window.bind(on_drop_file=self._on_drop_file)
        return sm
    
    def _on_drop_file(self, window, filepath, x, y):
        print(f"File dropped: {filepath.decode('utf-8')}")
        pass


if __name__ == '__main__':
    ImageCatalogApp().run()
