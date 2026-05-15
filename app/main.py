import asyncio
from kivy.app import App
from kivy.uix.label import Label
import httpx

class ImgOrgApp(App):
    def build(self):
        self.label = Label(text="Connecting to Bridge...")
        return self.label

    # This replaces the old 'run()' method
    async def app_func(self):
        async def run_wrapper():
            # We must await the app's start/build
            await self.async_run(async_lib='asyncio')
            print("App stopped")

        # Start the network check and the app simultaneously
        await asyncio.gather(run_wrapper(), self.check_bridge())

    async def check_bridge(self):
        # Give the API a moment to boot up
        await asyncio.sleep(2) 
        
        async with httpx.AsyncClient() as client:
            try:
                # Use 127.0.0.1 instead of localhost to avoid IPv6 conflicts
                response = await client.get("http://127.0.0.1:8000/health", timeout=5.0)
                data = response.json()
                self.label.text = f"Bridge {data['status']} - Version {data['version']}"
            except Exception as e:
                self.label.text = f"Bridge Offline: {str(e)}"

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ImgOrgApp().app_func())
    loop.close()