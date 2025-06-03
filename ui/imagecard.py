from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import DictProperty, ObjectProperty, StringProperty, BooleanProperty, NumericProperty

import time

from catalog.thumbnail import ensure_thumbnail

class ClickableImage(ButtonBehavior, Image):
    """An Image that can be clicked like a button"""
    
    def __init__(self, on_click=None, **kwargs):
        self.register_event_type('on_single_click')
        self.register_event_type('on_double_click')
        super().__init__(**kwargs)
        self._last_click_time = 0

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.button == 'left':
            now = time.time()
            modifiers = list(Window.modifiers)

            if now - self._last_click_time < 0.2:
                if self._click_event:
                    self._click_event.cancel()
                    self._click_event = None
                    self.dispatch('on_double_click', modifiers)
            else:
                self._click_event = Clock.schedule_once(lambda dt: self.dispatch('on_single_click', modifiers), 0.2)
                # if self.on_click:
                #     self.on_click(touch)

            self._last_click_time = now
            return True
        return super().on_touch_down(touch)


    def on_single_click(self, modifiers):
        print(f"Click", end=" ")
        for m in modifiers:
            print(m, end=" ")
        print()

    def on_double_click(self, modifiers):
        print(f"Click click", end=" ")
        for m in modifiers:
            print(m, end=" ")
        print()

from kivy.factory import Factory
Factory.register('ClickableImage', cls=ClickableImage)

from kivy.lang import Builder
Builder.load_file("ui/imagecard.kv")

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

