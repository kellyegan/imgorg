from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import DictProperty, ObjectProperty, StringProperty
from kivy.metrics import dp

from kivy.lang import Builder
Builder.load_file("ui/imagecard.kv")

from catalog.thumbnail import ensure_thumbnail

class ClickableImage(ButtonBehavior, Image):
    """An Image that can be clicked like a button"""
    pass

class ImageCard(BoxLayout):
    image_data = DictProperty()
    on_click = ObjectProperty(None)
    thumb_source = StringProperty()

    def __init__(self, image_data, index=None, on_click=None, **kwargs):
        super().__init__(**kwargs)
        self.image_data = image_data
        self.index = index
        self.on_click = on_click

        thumb_path = ensure_thumbnail(image_data['path'])
        if thumb_path is not None:
            self.thumb_source = thumb_path

    def _on_image_click(self, *args):
        if self.index is not None:
            app = App.get_running_app()
            app.set_index(self.index)
