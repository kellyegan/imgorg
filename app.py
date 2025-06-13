from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import Config
from kivy.clock import Clock


from kivy.properties import ListProperty, NumericProperty

from ui.thumbnailbrowserscreen import ThumbnailBrowserScreen
from ui.imagepreviewscreen import ImagePreviewScreen
from ui.importscreen import ImportScreen

from catalog.db import get_all_images, add_image_list, find_catalog_duplicates   # You must have this function in catalog/db.py

Config.set('kivy', 'exit_on_escape', '0')

class ImgOrgApp(App):
    image_list = ListProperty([])
    active_index = NumericProperty(None)
    selected_indexes = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drop_buffer = []
        self._drop_timer = None

    def build(self):
        Builder.load_file("ui/thumbnailbrowserscreen.kv")
        Builder.load_file("ui/imagepreviewscreen.kv")
        Builder.load_file("ui/importscreen.kv")

        Window.bind(on_drop_file=self._on_drop_file)
        
        Window.size = (1024, 1024)
        Window.top = 50
        Window.left = 10

        self.sm = ScreenManager()
        self.sm.add_widget(ThumbnailBrowserScreen())
        self.sm.add_widget(ImagePreviewScreen())
        self.sm.add_widget(ImportScreen())

        self.image_list = get_all_images()
        self.active_index = 0

        return self.sm
    
    def view_image_preview(self, index):
        self.set_active(index)
        self.sm.transition.direction = 'up'
        self.sm.current = "preview"

    def view_thumbnail_browser(self):
        self.sm.transition.direction = 'down'
        self.sm.current = "browser"

    def view_import_screen(self):
        self.sm.transition.direction = 'left'
        self.sm.current = "import"

    def _on_drop_file(self, window, filepath, x, y):
        # Don't allow drop files while import screen is visible
        if self.sm.current == "import":
            return
        
        path_string = filepath.decode('utf-8')

        self.drop_buffer.append(path_string)

        if self._drop_timer:
            self._drop_timer.cancel()

        # Wait 100ms to allow all dropfile event to accumulate
        self._drop_timer = Clock.schedule_once(self._handle_drop_buffer, 0.1)

    def _handle_drop_buffer(self, dt):
        # Setup import screen
        import_screen = self.root.get_screen("import")
        import_screen.process_import_paths(self.drop_buffer)

        self.drop_buffer = []
        self._drop_timer = None

        self.view_import_screen()
        
    def set_active(self, index):
        if index < 0 or index >= len(self.image_list):
            return
        self.active_index = index

    def select_index(self, index):
        if index < 0 or index >= len(self.image_list):
            return
        if index not in self.selected_indexes:
            self.selected_indexes.append(index)

    def deselect_index(self, index):
        if index in self.selected_indexes:
            self.selected_indexes.remove(index)

    def toggle_selection(self, index):
        if index in self.selected_indexes:
            self.deselect_index(index)
        else:
            self.select_index(index)
            
    def selected_all_indexes(self):
        self.selected_indexes = [i for i in range(len(self.image_list))]

    def deselect_all_indexes(self):
        self.selected_indexes = []

    def select_between_active_and_index(self, index):
        start = index if index < self.active_index else self.active_index
        end = index if index > self.active_index else self.active_index

        for i in range(start, end + 1):
            self.select_index(i)

if __name__ == "__main__":
    ImgOrgApp().run()