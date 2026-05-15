# bridge/main.py (Update)
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse
from .database import init_db, get_db
from .scanner import scan_directory

app = FastAPI()
init_db()

@app.get("/images")
def list_images():
    conn = get_db()
    images = conn.execute("SELECT * FROM images").fetchall()
    conn.close()
    return [dict(row) for row in images]

@app.post("/scan")
async def start_scan(path: str, background_tasks: BackgroundTasks):
    # In a real app, we'd track status, but let's keep it simple
    background_tasks.add_task(scan_directory, path)
    return {"message": "Scanning started"}

@app.get("/thumbnail/{image_id}")
def get_thumbnail(image_id: int):
    conn = get_db()
    image = conn.execute("SELECT path FROM images WHERE id = ?", (image_id,)).fetchone()
    conn.close()
    if image:
        # For Phase 1, we serve the full image. 
        # (We'll add Pillow resizing here in the next iteration).
        return FileResponse(image['path'])
    return {"error": "Not found"}