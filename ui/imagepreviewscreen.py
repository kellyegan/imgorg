from kivy.uix.screenmanager import Screen
from kivy.properties import DictProperty
from kivy.core.window import Window
from kivy.app import App

class ImagePreviewScreen(Screen):
    # Reactive property bound to your .kv file layout
    current_image = DictProperty(None, allownone=True)

    def __init__(self, **kw):
        super().__init__(**kw)
        Window.bind(on_key_down=self._on_key_down)
        self.app = App.get_running_app()

    def on_pre_enter(self, *args):
        self._sync_current_image()
    
    # def on_enter(self):
    #     """Fires automatically when switching to the preview screen."""
    #     self._sync_current_image()

    def _sync_current_image(self):
        """Resolves the active image from the app's global state list."""
        if 0 <= self.app.active_index < len(self.app.image_list):
            self.current_image = self.app.image_list[self.app.active_index]
        else:
            self.current_image = None

    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        # Ignore keyboard inputs if this screen isn't actively displaying
        if self.manager.current != "preview":
            return False

        if key == 27:  # Escape key -> drop back to thumbnail browser
            self.manager.current = "browser"
            return True

        elif key == 276:  # Left arrow key -> previous image
            if self.app.active_index > 0:
                self.app.set_active(self.app.active_index - 1)
                self._sync_current_image()
            return True

        elif key == 275:  # Right arrow key -> next image
            if self.app.active_index < len(self.app.image_list) - 1:
                self.app.set_active(self.app.active_index + 1)
                self._sync_current_image()
            return True

        return False