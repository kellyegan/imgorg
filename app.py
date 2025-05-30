from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty

from ui.widgets import ImageCard

from catalog.db import get_all_images, add_image_list, check_catalog_duplicate  # You must have this function in catalog/db.py


Builder.load_file("ui/imgorg.kv")

class ImgOrgApp(App):
    image_list = ListProperty([])
    current_index = NumericProperty(-1)

    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(ThumbnailBrowserScreen())
        self.sm.add_widget(ImagePreviewScreen())

        Window.bind(on_drop_file=self._on_drop_file)
        
        self.image_list = get_all_images()
        print(f"In app image list length: {len(self.image_list)}")

        return self.sm
    
    def _on_drop_file(self, window, filepath, x, y):
        path_string = filepath.decode('utf-8')
        
class ImagePreviewScreen(Screen):
    pass       

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
        
    def load_image_grid(self, images):
        # Clear existing widgets in the grid layout
        self.ids["thumbnail_grid"].clear_widgets()

        if len(images) > 0:
            self.show_image_grid(True)
            for img in images:
                card = ImageCard(img)
                self.ids["thumbnail_grid"].add_widget(card)
        else:
            self.show_image_grid(False)

    def update_column_size(self, *args):
        """
        Update the number of columns based on available width.
        """
        Window.bind(on_resize=self.update_column_size)
        border_spacing = 10
        available_width = Window.width - border_spacing
        self.columns = max(1, int(available_width / self.thumbnail_width))
        
        self.ids["thumbnail_grid"].cols = self.columns

    def show_image_grid(self, show_grid):
        """
        Show the image grid when there are more than 0 images
        otherwise show a labels explaining how to add images
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