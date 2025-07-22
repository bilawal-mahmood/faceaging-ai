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
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "result": None,
                                                     "error": None,
                                                     "log": ""})


@app.post("/convert/", response_class=HTMLResponse)
async def convert_image(request: Request, file: UploadFile = File(...), conversion: str = Form(...)):
    log_msgs = []
    log_msgs.append("🟢 Received upload")

    contents = await file.read()
    log_msgs.append(f"Loaded file: {file.filename}, size {len(contents)} bytes")
    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        image_np = np.array(image)
        log_msgs.append("Converted to numpy array")
    except Exception as e:
        log_msgs.append(f"❌ Error loading image: {e}")
        return templates.TemplateResponse("index.html", {"request": request, "result": None, "error": "Invalid image file", "log": "\\n".join(log_msgs)})

    faces = extract_faces_opencv(image_np)
    log_msgs.append(f"Faces detected: {len(faces)}")

    if not faces:
        return templates.TemplateResponse("index.html", {"request": request, "result": None, "error": "No face detected", "log": "\\n".join(log_msgs)})

    face = cv2.resize(faces[0], (256, 256))
    log_msgs.append("Resized face to 256x256")

    try:
        if conversion == "young_to_old":
            result = generate_Y2O(face)
        else:
            result = generate_O2Y(face)
        log_msgs.append(f"Applied model: {conversion}")
    except Exception as e:
        log_msgs.append(f"❌ Error during model processing: {e}")
        return templates.TemplateResponse("index.html", {"request": request, "result": None, "error": "Processing error", "log": "\\n".join(log_msgs)})

    result_img = (result * 255).astype(np.uint8)
    _, buffer = cv2.imencode(".png", result_img[:, :, ::-1])
    base64_img = base64.b64encode(buffer).decode("utf-8")
    log_msgs.append("Generated base64 image result")

    full_log = "\\n".join(log_msgs)
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "result": base64_img,
                                                     "error": None,
                                                     "log": full_log})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
