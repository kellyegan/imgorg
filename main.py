from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from catalog.db import get_all_images, add_image_list, check_catalog_duplicate  # You must have this function in catalog/db.py
from ui.widgets import ImageCard       # This needs to be defined as in Step 3
from catalog.image_importer import scan_for_images


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

def prompt_for_duplicates(new_path, existing_image):
    box = BoxLayout(orientation='vertical', spacing=10, padding=10)
    label = Label(text=f"Duplicate image detected:\n\n{new_path}\n\nAlready in catalog as:\n{existing_image['path']}")
    btn_ignore = Button(text="Ignore", size_hint_y=None, height=40)
    btn_add_anyway = Button(text="Add anyway", size_hint_y=None, height=40)

    popup = Popup(title="Duplicate Detected", content=box, size_hint=(0.8, 0.6))
    
    def on_ignore(instance):
        popup.dismiss()

    def on_add(instance):
        popup.dismiss()
        # Insert anyway, possibly with a flag or just proceed
        # You can modify the DB function to allow forced insert
        # force_add_duplicate(new_path)

    btn_ignore.bind(on_press=on_ignore)
    btn_add_anyway.bind(on_press=on_add)

    box.add_widget(label)
    box.add_widget(btn_add_anyway)
    box.add_widget(btn_ignore)
    popup.open()


if __name__ == '__main__':
    ImageCatalogApp().run()
