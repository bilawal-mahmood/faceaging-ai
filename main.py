from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from helper import *
from PIL import Image
import numpy as np
import io
import cv2
import base64

app = FastAPI()

# CORS for JS frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/convert/")
async def convert_image(file: UploadFile = File(...), conversion: str = Form(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    image_np = np.array(image)

    faces = extract_faces_opencv(image_np)
    if not faces:
        return {"error": "No face detected"}

    face = cv2.resize(faces[0], (256, 256))  # process only 1 face for now

    if conversion == "young_to_old":
        result = generate_Y2O(face)
    elif conversion == "old_to_young":
        result = generate_O2Y(face)
    else:
        return {"error": "Invalid conversion type"}

    # Convert to base64
    result_img = (result * 255).astype(np.uint8)
    _, buffer = cv2.imencode(".png", result_img[:, :, ::-1])  # BGR to RGB
    base64_img = base64.b64encode(buffer).decode("utf-8")

    return {"image": base64_img}
