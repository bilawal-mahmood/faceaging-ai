from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
import io
import cv2
import numpy as np
import base64
from helper import extract_faces_opencv, generate_Y2O, generate_O2Y

app = FastAPI()

# CORS for JS frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/convert/", response_class=HTMLResponse)
async def convert(file: UploadFile = File(...), conversion: str = Form(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        image_np = np.array(image)

        faces = extract_faces_opencv(image_np)
        if not faces:
            return HTMLResponse("<h2>No face detected</h2>", status_code=400)

        face = cv2.resize(faces[0], (256, 256))

        if conversion == "young_to_old":
            result = generate_Y2O(face)
        elif conversion == "old_to_young":
            result = generate_O2Y(face)
        else:
            return HTMLResponse("<h2>Invalid conversion type</h2>", status_code=400)

        # Convert model result to image
        result_img = (result * 255).astype(np.uint8)
        _, buffer = cv2.imencode(".png", result_img[:, :, ::-1])  # Convert to RGB
        img_str = base64.b64encode(buffer).decode("utf-8")

        return f"""
        <html><body>
            <img src="data:image/png;base64,{img_str}" style="max-width:100%; border-radius:20px; box-shadow:0 4px 20px rgba(0,0,0,0.2);" />
        </body></html>
        """

    except Exception as e:
        return HTMLResponse(f"<h2>Error: {str(e)}</h2>", status_code=500)
