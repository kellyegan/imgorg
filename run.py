import multiprocessing
import uvicorn
import time
import asyncio
from bridge.main import app
from app.main import ImgOrgApp

def start_api():
    # Use a low-level uvicorn config to ensure it handles signals well
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="error")
    server = uvicorn.Server(config)
    server.run()

def start_ui():
    ui_app = ImgOrgApp()
    asyncio.run(ui_app.app_func())

if __name__ == "__main__":
    multiprocessing.freeze_support()
    
    # Use 'spawn' instead of 'fork' for consistency across OSs
    multiprocessing.set_start_method('spawn', force=True)

    api_proc = multiprocessing.Process(target=start_api)
    api_proc.start()
    
    try:
        start_ui()
    except KeyboardInterrupt:
        pass
    finally:
        print("Closing Bridge...")
        api_proc.terminate()
        api_proc.join(timeout=2)
        if api_proc.is_alive():
            api_proc.kill() # Force kill if it won't die
        print("Goodbye.")