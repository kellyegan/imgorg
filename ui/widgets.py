from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior

from catalog.thumbnail import ensure_thumbnail

class ClickableImage(ButtonBehavior, Image):
    """An Image that can be clicked like a button"""
    pass

class ImageCard(BoxLayout):

    def __init__(self, image_data, index=None, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, height=200, **kwargs)
        self.image_data = image_data
        self.index = index

        thumb_path = ensure_thumbnail(image_data['path'])
        if thumb_path is None:
            return  # skip broken image

        img_widget = ClickableImage(source=thumb_path, allow_stretch=True, keep_ratio=True)
        img_widget.bind(on_release=self._on_image_click)
        label = Label(text=image_data['filename'], size_hint_y=0.2, font_size=10)

        self.add_widget(img_widget)
        self.add_widget(label)

    def _on_image_click(self, instance, *args):
        
        
        print(self.image_data['path'])
        if self.index is not None:
            print(self.index)
            app = App.get_running_app()
            app.set_index(self.index)
