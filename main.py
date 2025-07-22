from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from PIL import Image
import io, base64, os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/convert/", response_class=HTMLResponse)
async def convert(request: Request, file: UploadFile = File(...), conversion: str = Form(...)):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Dummy transformation
        image = image.convert("L").convert("RGB")

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return templates.TemplateResponse("index.html", {
            "request": request,
            "result_image": f"data:image/jpeg;base64,{img_str}",
        })
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": str(e),
        })
