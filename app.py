from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.lang import Builder

Builder.load_file("ui/imgorg.kv")

class ImgOrgApp(App):
    imagelist = []

    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(ThumbnailBrowserScreen())
        self.sm.add_widget(ImagePreviewScreen())
        return self.sm

class ThumbnailBrowserScreen(Screen):
    columns = 1
    thumbnail_width = 200

    def __init__(self, **kw):
        super().__init__(**kw)
        Window.bind(size=self.update_column_size)
        self.update_column_size()

    def update_column_size(self, *args):
        """
        Update the number of columns based on available width.
        """
        Window.bind(on_resize=self.update_column_size)
        border_spacing = 10
        available_width = Window.width - border_spacing
        self.columns = max(1, int(available_width / self.thumbnail_width))
        
        self.ids["thumbnail_grid"].cols = self.columns

    def show_image_grid(self, count):
        """
        Show the image grid when there are more than 0 images
        otherwise show a labels explaining how to add images
        """
        hide_id = "scroll_area" if count <= 0 else "images_empty_label"
        show_id = "images_empty_label" if count <= 0 else "scroll_area"
        self.ids[hide_id].opacity = 0
        self.ids[hide_id].height = 0
        self.ids[hide_id].size_hint_y = None
        self.ids[show_id].opacity = 1
        self.ids[show_id].height = 100
        self.ids[show_id].size_hint_y = 1
    
    def on_pre_enter(self):
        self.show_image_grid(1)
    
class ImagePreviewScreen(Screen):
    pass

if __name__ == "__main__":
    ImgOrgApp().run()