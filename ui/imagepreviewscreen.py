from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock

from kivy.properties import StringProperty

class ImagePreviewScreen(Screen):
    image_source = StringProperty("")

    def __init__(self, **kw):
        super().__init__(**kw)
        self.current_image = None

        Window.bind(on_key_down=self._on_key_down)
        app = App.get_running_app()
        app.bind(active_index=self._on_active_index_change)

    def on_pre_enter(self):
        app = App.get_running_app()
        self._on_active_index_change(app, app.active_index)
        
    def _on_active_index_change(self, instance, value):
        if not isinstance(value, int):
            return
        
        self.current_image = instance.image_list[value]
        self.image_source = self.current_image["path"]

    def _on_key_down(self, window, key, scancode, codepoint, modifier):
        if self.manager.current != "preview":
            return
        
        app = App.get_running_app()
        num_images = len(app.image_list)

        if key in (27, 32):  # Escape key
            Clock.schedule_once(lambda dt: app.view_thumbnail_browser(), 0.05)
        elif key == 276:  # Left arrow key
            new_index = (app.active_index - 1) % num_images
            app.set_active(new_index)
        elif key == 275:  # Right arrow key
            new_index = (app.active_index + 1) % num_images
            app.set_active(new_index)