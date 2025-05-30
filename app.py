from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import Config

from kivy.uix.image import Image
from kivy.properties import ListProperty, NumericProperty, ObjectProperty

from ui.widgets import ImageCard

from catalog.db import get_all_images, add_image_list, check_catalog_duplicate  # You must have this function in catalog/db.py
from catalog.image_importer import scan_for_images

Config.set('kivy', 'exit_on_escape', '0')
Builder.load_file("ui/imgorg.kv")

class ImgOrgApp(App):
    image_list = ListProperty([])
    current_index = NumericProperty(1)

    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(ThumbnailBrowserScreen())
        self.sm.add_widget(ImagePreviewScreen())

        Window.bind(on_drop_file=self._on_drop_file)

        self.image_list = get_all_images()
        self.current_index = 0

        return self.sm
    
    def set_index(self, index):
        if 0 <= index < len(self.image_list):
            self.current_index = index
            self.sm.transition.direction = 'up'
            self.sm.current = "preview"
    
    def _on_drop_file(self, window, filepath, x, y):
        path_string = filepath.decode('utf-8')
        images, import_duplicates = scan_for_images(path_string)
        imports, catalog_duplicates = check_catalog_duplicate(images)

        add_image_list(imports)

        self.image_list = get_all_images()
        
        
class ImagePreviewScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        Window.bind(on_key_down=self.on_key_down)

    def on_pre_enter(self):
        app = App.get_running_app()
        self.ids["preview_box"].clear_widgets()
        app.bind(current_index=self.on_current_index_change)
        self.on_current_index_change(app, app.current_index)
        
        
    def on_current_index_change(self, instance, value):
        if not isinstance(value, int):
            return
        
        if value < 0 or value >= len(instance.image_list):
            print("Index out of bounds")
            return
        
        self.current_image = instance.image_list[value]

        self.ids.preview_box.clear_widgets()
        image_widget = Image(source=self.current_image["path"], allow_stretch=True, keep_ratio=True)    
        self.ids.preview_box.add_widget(image_widget)

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        if self.manager.current != "preview":
            return
        app = App.get_running_app()

        if key == 27:  # Escape key
            self.manager.transition.direction = 'down'
            self.manager.current = "browser"
        elif key == 276:  # Left arrow key
            new_index = (app.current_index - 1) % len(app.image_list)
            app.set_index(new_index)
        elif key == 275:  # Right arrow key
            new_index = (app.current_index + 1) % len(app.image_list)
            app.set_index(new_index)

class ThumbnailBrowserScreen(Screen):
    columns = 1
    thumbnail_width = 200

    def __init__(self, **kw):
        super().__init__(**kw)
        Window.bind(size=self.update_column_size)
        self.update_column_size()

    def on_enter(self):
        app = App.get_running_app()
        app.bind(image_list=self.on_image_list_change)
        self.on_image_list_change(app, app.image_list)

    def on_image_list_change(self, instance, value):
        image_list = value
        self.load_image_grid(image_list)

    def update_column_size(self, *args):
        """
        Update the number of columns based on available width.
        """
        Window.bind(on_resize=self.update_column_size)
        border_spacing = 10
        available_width = Window.width - border_spacing
        self.columns = max(1, int(available_width / self.thumbnail_width))
        
        self.ids["thumbnail_grid"].cols = self.columns
       
    def load_image_grid(self, images):
        # Clear existing widgets in the grid layout
        self.ids["thumbnail_grid"].clear_widgets()

        if len(images) > 0:
            self.show_image_grid(True)
            for i, img in enumerate(images):
                card = ImageCard(img, i)
                self.ids["thumbnail_grid"].add_widget(card)
        else:
            self.show_image_grid(False)

    def show_image_grid(self, show_grid):
        """
        Show the image grid
        """
        hide_id = "images_empty_label" if show_grid else "scroll_area"
        show_id = "scroll_area" if show_grid else "images_empty_label"
        self.ids[hide_id].opacity = 0
        self.ids[hide_id].height = 0
        self.ids[hide_id].size_hint_y = None
        self.ids[show_id].opacity = 1
        self.ids[show_id].height = 100
        self.ids[show_id].size_hint_y = 1
    
    def on_pre_enter(self):
        self.show_image_grid(1)

if __name__ == "__main__":
    ImgOrgApp().run()