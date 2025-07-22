from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request

from helper import extract_faces_opencv, generate_Y2O, generate_O2Y
from PIL import Image

import numpy as np
import io, cv2, base64, os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    # No result yet
    return templates.TemplateResponse("index.html", {"request": request, "result": None})


@app.post("/convert/", response_class=HTMLResponse)
async def convert_image(request: Request, file: UploadFile = File(...), conversion: str = Form(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    image_np = np.array(image)
    faces = extract_faces_opencv(image_np)
    if not faces:
        return templates.TemplateResponse("index.html", {"request": request, "result": None, "error": "No face detected"})

    face = cv2.resize(faces[0], (256, 256))
    if conversion == "young_to_old":
        result = generate_Y2O(face)
    elif conversion == "old_to_young":
        result = generate_O2Y(face)
    else:
        return templates.TemplateResponse("index.html", {"request": request, "result": None, "error": "Invalid type"})

    result_img = (result * 255).astype(np.uint8)
    _, buffer = cv2.imencode(".png", result_img[:, :, ::-1])
    base64_img = base64.b64encode(buffer).decode("utf-8")

    return templates.TemplateResponse("index.html", {"request": request, "result": base64_img, "error": None})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
