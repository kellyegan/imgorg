import asyncio
import httpx

from kivy.app import App
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import Config
from kivy.clock import Clock

from kivy.properties import ListProperty, NumericProperty

from ui.thumbnailbrowserscreen import ThumbnailBrowserScreen
from ui.imagepreviewscreen import ImagePreviewScreen
from ui.importscreen import ImportScreen

Config.set('kivy', 'exit_on_escape', '0')

class ImageGrid(RecycleView):
    pass

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

        self.update_image_list()
        self.active_index = 0

        return self.sm

    def update_image_list(self):
        # TODO: Replace with actual image list retrieval logic (maybe async)
        # self.image_list = get_all_images()
        pass
    
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
        print(f"Files dropped {len(self.drop_buffer)}")
        # Setup import screen
        import_screen = self.root.get_screen("import")
        import_screen.process_import_paths(self.drop_buffer)

        self.drop_buffer = []
        self._drop_timer = None

        self.view_import_screen()
        pass

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

    def on_stop(self):
        # This signals the background loops to stop immediately
        self.running = False

    async def app_func(self):
        self.running = True
        # Create the tasks so we can manage them
        ui_task = asyncio.create_task(self.async_run(async_lib='asyncio'))
        poll_task = asyncio.create_task(self.fetch_images())
        
        # Wait for the UI to close
        await ui_task
        
        # Once UI is closed, cancel the poller and wait for it to clean up
        poll_task.cancel()
        try:
            await poll_task
        except asyncio.CancelledError:
            pass
        print("UI and background tasks cleaned up.")

    async def fetch_images(self):
        # Wait a moment for the bridge to be ready
        await asyncio.sleep(2)
        
        async with httpx.AsyncClient() as client:
            last_count = 0
            # Use 'self.running' to check if we should keep polling
            while self.running:
                try:
                    response = await client.get("http://127.0.0.1:8000/images", timeout=2.0)
                    fetched_images = response.json()
                    
                    if len(fetched_images) != last_count:
                        # Ensure we don't try to update if the root widget is gone
                        if self.root:
                            self.root.data = [{'source': f"http://127.0.0.1:8000/thumbnail/{img['id']}"} for img in fetched_images]
                            last_count = len(fetched_images)
                except Exception as e:
                    print(f"Polling error: {e}")
                
                # Use a shorter sleep but check 'self.running' frequently
                for _ in range(30): 
                    if not self.running: break
                    await asyncio.sleep(0.1)


if __name__ == "__main__":
    ImgOrgApp().run()