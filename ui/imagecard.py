from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import DictProperty, ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.metrics import dp

from kivy.lang import Builder
Builder.load_file("ui/imagecard.kv")

from catalog.thumbnail import ensure_thumbnail

class ClickableImage(ButtonBehavior, Image):
    """An Image that can be clicked like a button"""
    pass

class ImageCard(BoxLayout):
    image_data = DictProperty()
    index = NumericProperty()
    on_click = ObjectProperty(None)
    thumb_source = StringProperty()
    is_active = BooleanProperty(False)
    is_selected = BooleanProperty(False)

    def __init__(self, image_data, index=None, is_active=False, is_selected=False, on_click=None, **kwargs):
        super().__init__(**kwargs)
        self.image_data = image_data
        self.index = index
        self.on_click = on_click
        self.is_active = is_active
        self.is_selected = is_selected

        thumb_path = ensure_thumbnail(image_data['path'])
        if thumb_path is not None:
            self.thumb_source = thumb_path

    def _on_image_click(self, *args):
        if self.index is not None:
            app = App.get_running_app()
            app.preview_image_at_index(self.index)

    def set_active(self, active):
        self.is_active = active

    def set_selected(self, selected):
        self.is_selected = selected

