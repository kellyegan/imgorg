from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

from catalog.db import get_all_images  # You must have this function in catalog/db.py
from ui.widgets import ImageCard       # This needs to be defined as in Step 3

# Load the Kivy layout for MainScreen
Builder.load_file('ui/main_screen.kv')


class MainScreen(Screen):
    def on_pre_enter(self):
        self.ids.image_grid.clear_widgets()
        images = get_all_images()

        for img in images:
            card = ImageCard(img)
            self.ids.image_grid.add_widget(card)


class ImageCatalogApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        return sm


if __name__ == '__main__':
    ImageCatalogApp().run()
