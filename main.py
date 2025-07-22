from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from PIL import Image
import io
import base64

app = FastAPI()

# Allow CORS for any frontend to access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files and HTML templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/convert/", response_class=HTMLResponse)
async def convert_image(
    request: Request,
    file: UploadFile = File(...),
    conversion: str = Form(...)
):
    try:
        # Read uploaded image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Simulated conversion (grayscale)
        if conversion == "grayscale":
            image = image.convert("L").convert("RGB")

        # Convert image to base64
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        return templates.TemplateResponse("index.html", {
            "request": request,
            "result_image": f"data:image/jpeg;base64,{img_base64}",
            "success": True
        })

    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": str(e)
        })
