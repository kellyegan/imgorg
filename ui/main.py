import asyncio
from kivy.app import App
from kivy.uix.recycleview import RecycleView
import httpx

class ImageGrid(RecycleView):
    pass

class ImgOrgApp(App):
    def build(self):
        return ImageGrid()

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
                    new_data = response.json()
                    
                    if len(new_data) != last_count:
                        # Ensure we don't try to update if the root widget is gone
                        if self.root:
                            self.root.data = [{'source': f"http://127.0.0.1:8000/thumbnail/{img['id']}"} for img in new_data]
                            last_count = len(new_data)
                except Exception as e:
                    print(f"Polling error: {e}")
                
                # Use a shorter sleep but check 'self.running' frequently
                for _ in range(30): 
                    if not self.running: break
                    await asyncio.sleep(0.1)