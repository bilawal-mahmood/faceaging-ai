from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from helper import extract_faces_opencv, generate_Y2O, generate_O2Y

from PIL import Image
import numpy as np
import io
import cv2
import base64

app = FastAPI()

# Allow frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/convert/")
async def convert_image(file: UploadFile = File(...), conversion: str = Form(...)):
    contents = await file.read()

    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        image_np = np.array(image)

        # Detect face
        faces = extract_faces_opencv(image_np)
        if not faces:
            return {"error": "No face detected in image."}

        face = cv2.resize(faces[0], (256, 256))

        # Apply model based on conversion type
        if conversion == "young_to_old":
            result = generate_Y2O(face)
        elif conversion == "old_to_young":
            result = generate_O2Y(face)
        else:
            return {"error": "Invalid conversion type"}

        # Convert to base64 for frontend
        result_img = (result * 255).astype(np.uint8)
        _, buffer = cv2.imencode(".png", result_img[:, :, ::-1])  # BGR → RGB
        base64_img = base64.b64encode(buffer).decode("utf-8")

        return {"image": base64_img}

    except Exception as e:
        return {"error": f"Processing error: {str(e)}"}
