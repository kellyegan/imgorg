from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from catalog.thumbnail import ensure_thumbnail

class ImageCard(BoxLayout):
    def __init__(self, image_data, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, height=200, **kwargs)

        thumb_path = ensure_thumbnail(image_data['path'])
        if thumb_path is None:
            return  # skip broken image

        img_widget = Image(source=thumb_path, allow_stretch=True, keep_ratio=True)
        label = Label(text=image_data['filename'], size_hint_y=0.2, font_size=10)

        self.add_widget(img_widget)
        self.add_widget(label)
