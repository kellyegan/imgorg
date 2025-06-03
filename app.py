from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import Config
from kivy.clock import Clock
from kivy.metrics import dp

from kivy.uix.image import Image
from kivy.properties import ListProperty, NumericProperty, ObjectProperty

from ui.imagecard import ImageCard

from catalog.db import get_all_images, add_image_list, check_catalog_duplicate  # You must have this function in catalog/db.py
from catalog.image_importer import scan_for_images

Config.set('kivy', 'exit_on_escape', '0')
Builder.load_file("ui/imgorg.kv")

class ImgOrgApp(App):
    image_list = ListProperty([])
    active_index = NumericProperty(None)

    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(ThumbnailBrowserScreen())
        self.sm.add_widget(ImagePreviewScreen())

        self.image_list = get_all_images()
        self.active_index = 0

        return self.sm
    
    def preview_image_at_index(self, index):
        self.set_active(index)
        self.sm.transition.direction = 'up'
        self.sm.current = "preview"

    def view_thumbnail_browser(self, dt):
        self.sm.transition.direction = 'down'
        self.sm.current = "browser"        

    def set_active(self, index):
        if 0 <= index < len(self.image_list):
            self.active_index = index

    def add_images_from_path(self, filepath):
        images, import_duplicates = scan_for_images(filepath)
        imports, catalog_duplicates = check_catalog_duplicate(images)
        add_image_list(imports)
        self.image_list = get_all_images()

        
class ImagePreviewScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        Window.bind(on_key_down=self._on_key_down)
        app = App.get_running_app()
        app.bind(active_index=self._on_active_index_change)

    def on_pre_enter(self):
        app = App.get_running_app()
        self.ids["preview_box"].clear_widgets()
        self._on_active_index_change(app, app.active_index)
        
    def _on_active_index_change(self, instance, value):
        if not isinstance(value, int):
            return
        
        if value < 0 or value >= len(instance.image_list):
            print("Index out of bounds")
            return
        
        self.current_image = instance.image_list[value]

        self.ids.preview_box.clear_widgets()
        image_widget = Image(source=self.current_image["path"], fit_mode="contain")
        # If you don't want to use scale up image use 'scale-down' instead
        # image_widget = Image(source=self.current_image["path"], fit_mode="scale-down")
        
        self.ids.preview_box.add_widget(image_widget)

    def _on_key_down(self, window, key, scancode, codepoint, modifier):
        if self.manager.current != "preview":
            return
        
        app = App.get_running_app()
        num_images = len(app.image_list)

        if key in (27, 32):  # Escape key
            Clock.schedule_once(app.view_thumbnail_browser, 0.05)
        elif key == 276:  # Left arrow key
            new_index = (app.active_index - 1) % num_images
            app.set_active(new_index)
        elif key == 275:  # Right arrow key
            new_index = (app.active_index + 1) % num_images
            app.set_active(new_index)

class ThumbnailBrowserScreen(Screen):
    columns = 1
    thumbnail_width = dp(200)

    def __init__(self, **kw):
        super().__init__(**kw)
        Window.bind(size=self._update_column_size)
        Window.bind(on_drop_file=self._on_drop_file)
        Window.bind(on_key_down=self._on_key_down)
        app = App.get_running_app()
        app.bind(active_index=self._on_active_index_change)

        Window.size = (1024, 1024)

    def on_enter(self):
        app = App.get_running_app()
        app.bind(image_list=self._on_image_list_change)
        self._on_image_list_change(app, app.image_list)
        
        Clock.schedule_once(self._wait_for_layout_ready, 0.1)

    def _wait_for_layout_ready(self, dt):
        if self.ids.thumbnail_grid.height == 0:
            Clock.schedule_once(self._wait_for_layout_ready, 0.05)
        else:
            Clock.schedule_once(self.scroll_to_current_thumb, 0.0)

    def _on_image_list_change(self, instance, value):
        image_list = value
        self.load_image_grid(image_list)

    def _on_drop_file(self, window, filepath, x, y):
        path_string = filepath.decode('utf-8')
        app = App.get_running_app()
        app.add_images_from_path(path_string)

    def scroll_to_current_thumb(self, dt):
        app = App.get_running_app()
        index = app.active_index

        grid = self.ids.thumbnail_grid
        scrollview = self.ids.scroll_area

        if grid.height <= scrollview.height:
            return

        try:
            target_widget = grid.children[::-1][index]
            scrollview.scroll_to(target_widget, padding=10)
        except IndexError:
            pass

    def _update_column_size(self, *args):
        """
        Update the number of columns based on available width.
        """
        border_spacing = dp(50)
        available_width = Window.width - border_spacing
        self.columns = max(1, int(available_width / self.thumbnail_width))

        # If there are less images than columns, resize the grid to fit the images
        app = App.get_running_app()
        image_count = len(app.image_list)
        if image_count > 0 and  image_count < self.columns:
            print( image_count, self.columns, image_count / self.columns)
            self.size_hint_x = image_count / self.columns
        else:
            self.size_hint_x = 1
        
        
        self.ids.thumbnail_grid.cols = self.columns
       
    def load_image_grid(self, images):
        # Clear existing widgets in the grid layout
        self.ids.thumbnail_grid.clear_widgets()
        app = App.get_running_app()

        if len(images) > 0:
            for i, img in enumerate(images):
                card = ImageCard(img, i, is_active = (i == app.active_index))
                self.ids.thumbnail_grid.add_widget(card)
        Clock.schedule_once(self._update_column_size, 0.1)

    def _on_active_index_change(self, instance, value):
        if not isinstance(value, int):
            return
        
        if self.manager.current != "browser":
            return        
        
        app = App.get_running_app()

        for thumb in self.ids.thumbnail_grid.children:
            if thumb.index == app.active_index:
                thumb.set_active(True)
            else:
                thumb.set_active(False)

    def _on_key_down(self, window, key, scancode, codepoint, modifier):
        if self.manager.current != "browser":
            return
        
        app = App.get_running_app()
        new_index = app.active_index

        if key == 276:  # Left arrow key
            new_index = app.active_index - 1
        elif key == 275:  # Right arrow key
            new_index = app.active_index + 1
        elif key == 273:  # Up arrow key
            new_index = app.active_index - self.columns     
        elif key == 274:  # Down arrow key
            new_index = app.active_index + self.columns
        elif key == 32:  # Space bar
            app.preview_image_at_index(app.active_index)
            return

        if( new_index >= 0 and new_index < len(app.image_list)):
            app.set_active(new_index)

        self.scroll_to_current_thumb(None)

if __name__ == "__main__":
    ImgOrgApp().run()