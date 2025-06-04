from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock

class ImagePreviewScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        Window.bind(on_key_down=self._on_key_down)
        app = App.get_running_app()
        app.bind(active_index=self._on_active_index_change)

    def on_pre_enter(self):
        app = App.get_running_app()
        self.ids.preview_box.clear_widgets()
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