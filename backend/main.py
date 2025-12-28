from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import os
from engine import TweenEngine

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

engine = TweenEngine()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.post("/generate")
async def generate(image_a: UploadFile = File(...), image_b: UploadFile = File(...), prompt: str = Form(...)):
    path_a = os.path.join(UPLOAD_DIR, "a.png")
    path_b = os.path.join(UPLOAD_DIR, "b.png")
    
    with open(path_a, "wb") as buffer: shutil.copyfileobj(image_a.file, buffer)
    with open(path_b, "wb") as buffer: shutil.copyfileobj(image_b.file, buffer)

    # In a real scenario, 'prompt' would guide a ControlNet or Attention map
    frames = engine.generate_tween(path_a, path_b)
    
    urls = []
    for i, frame in enumerate(frames):
        fname = f"frame_{i}.png"
        frame.save(os.path.join(UPLOAD_DIR, fname))
        urls.append(f"http://localhost:8000/uploads/{fname}")

    return {"frames": urls}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)