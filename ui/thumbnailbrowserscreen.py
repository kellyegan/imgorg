from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp

from ui.imagecard import ImageCard

class ThumbnailBrowserScreen(Screen):
    columns = 1
    thumbnail_width = dp(200)

    def __init__(self, **kw):
        super().__init__(**kw)
        Window.bind(size=self._update_column_size)
        Window.bind(on_drop_file=self._on_drop_file)
        Window.bind(on_key_down=self._on_key_down)

        Window.size = (1024, 1024)
        Window.top = 50
        Window.left = 10

        app = App.get_running_app()
        app.bind(active_index=self._on_active_index_change)
        app.bind(selected_indexes=self._on_selected_change)

    def on_enter(self):
        app = App.get_running_app()
        app.bind(image_list=self._on_image_list_change)
        self._on_image_list_change(app, app.image_list)
        
        Clock.schedule_once(self._wait_for_layout_ready, 0.1)

    def check_selection(self):
        app = App.get_running_app()

        for thumb in self.ids.thumbnail_grid.children:
            if thumb.index == app.active_index:
                thumb.set_active(True)
            else:
                thumb.set_active(False)
            if thumb.index in app.selected_indexes:
                thumb.set_selected(True)
            else:
                thumb.set_selected(False)

    def _wait_for_layout_ready(self, dt):
        if self.ids.thumbnail_grid.height == 0:
            Clock.schedule_once(self._wait_for_layout_ready, 0.05)
        else:
            Clock.schedule_once(self.scroll_to_current_thumb, 0.0)

    def _on_image_list_change(self, instance, value):
        image_list = value
        self.load_image_grid(image_list)

    def _on_drop_file(self, window, filepath, x, y):
        path_string = filepath.decode('utf-8')
        app = App.get_running_app()
        app.add_images_from_path(path_string)

    def scroll_to_current_thumb(self, dt):
        app = App.get_running_app()
        index = app.active_index

        grid = self.ids.thumbnail_grid
        scrollview = self.ids.scroll_area

        if grid.height <= scrollview.height:
            return

        try:
            target_widget = grid.children[::-1][index]
            scrollview.scroll_to(target_widget, padding=10)
        except IndexError:
            pass

    def _update_column_size(self, *args):
        """
        Update the number of columns based on available width.
        """
        border_spacing = dp(50)
        available_width = Window.width - border_spacing
        self.columns = max(1, int(available_width / self.thumbnail_width))

        # If there are less images than columns, resize the grid to fit the images
        app = App.get_running_app()
        image_count = len(app.image_list)
        if image_count > 0 and  image_count < self.columns:
            print( image_count, self.columns, image_count / self.columns)
            self.size_hint_x = image_count / self.columns
        else:
            self.size_hint_x = 1
        
        
        self.ids.thumbnail_grid.cols = self.columns
       
    def load_image_grid(self, images):
        # Clear existing widgets in the grid layout
        self.ids.thumbnail_grid.clear_widgets()
        app = App.get_running_app()

        if len(images) > 0:
            for i, img in enumerate(images):
                card = ImageCard(img, i, is_active = (i == app.active_index), is_selected=(i in app.selected_indexes))
                self.ids.thumbnail_grid.add_widget(card)
        Clock.schedule_once(self._update_column_size, 0.1)

    def _on_active_index_change(self, instance, value):
        if not isinstance(value, int):
            return
        
        if self.manager.current != "browser":
            return        
        
        app = App.get_running_app()

        self.check_selection()
    
    def _on_selected_change(self, instance, value):
        app = App.get_running_app()

        self.check_selection()

    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        if self.manager.current != "browser":
            return
        
        app = App.get_running_app()
        new_index = app.active_index

        print(key)

        if key == 276:  # Left arrow key
            new_index = app.active_index - 1
        elif key == 275:  # Right arrow key
            new_index = app.active_index + 1
        elif key == 273:  # Up arrow key
            new_index = app.active_index - self.columns     
        elif key == 274:  # Down arrow key
            new_index = app.active_index + self.columns
        elif key == 32:  # Space bar
            app.view_image_preview(app.active_index)
            return
        elif key == 13: # Enter key
            app.toggle_selection(app.active_index)
        
        if 'meta' in modifiers:
            # print(key)
            if key == 97: # A
                app.selected_all_indexes()
            elif key == 100: # D
                app.deselect_all_indexes()

        if( new_index >= 0 and new_index < len(app.image_list)):
            app.set_active(new_index)

        self.scroll_to_current_thumb(None)

