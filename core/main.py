# bridge/main.py (Update)
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool
from .database import init_db, get_db
from .thumbnail import ensure_thumbnail

app = FastAPI()

init_db()

@app.get("/status")
def get_status():
    return {"status": "online", "version": "0.1.0"}

@app.get("/images")
def list_images():
    conn = get_db()
    images = conn.execute("SELECT * FROM images").fetchall()
    conn.close()
    return [dict(row) for row in images]

@app.get("/thumbnail/{image_id}")
async def get_thumbnail(image_id: int):
    conn = get_db()
    image_data = conn.execute("SELECT path FROM images WHERE id = ?", (image_id,)).fetchone()

    if image_data:
        thumb_path = await run_in_threadpool(ensure_thumbnail, image_id, image_data['path'])

        if thumb_path:
            return FileResponse(thumb_path)
    
    return {"error": "Image not found"}