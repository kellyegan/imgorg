from fastapi import FastAPI, BackgroundTasks
from .database import init_db

app = FastAPI(title="ImgOrg Bridge")
db = init_db()

@app.get("/health")
def health_check():
    return {"status": "online", "version": "0.1.0"}

@app.post("/scan")
async def start_scan(path: str, background_tasks: BackgroundTasks):
    # This will be implemented in Phase 1
    # background_tasks.add_task(run_file_scan, path)
    return {"message": f"Scan started for {path}"}