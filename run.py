import multiprocessing
import uvicorn
import time
from bridge.main import app
from app.main import ImgOrgApp
import asyncio

def start_api():
    # Bind to 0.0.0.0 to ensure it's reachable on all local interfaces
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

def start_ui():
    # Use the new async entry point we created above
    ui_app = ImgOrgApp()
    asyncio.run(ui_app.app_func())

if __name__ == "__main__":
    multiprocessing.freeze_support() # Important for Windows
    
    print("Starting Bridge...")
    api_proc = multiprocessing.Process(target=start_api)
    api_proc.start()
    
    # Wait a second to let the port open
    time.sleep(1)
    
    print("Starting UI...")
    try:
        start_ui()
    finally:
        print("Shutting down...")
        api_proc.terminate()
        api_proc.join()