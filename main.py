from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.templating import Jinja2Templates
from PIL import Image
import io
import base64
import os

app = FastAPI()

# CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/convert/", response_class=HTMLResponse)
async def convert(file: UploadFile = File(...), conversion: str = Form(...)):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Dummy transformation: Grayscale
        image = image.convert("L").convert("RGB")

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        html = f"""
        <html>
        <body>
            <img src="data:image/jpeg;base64,{img_str}" />
        </body>
        </html>
        """
        return HTMLResponse(content=html)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return HTMLResponse(content=f"<h2>Error: {str(e)}</h2>", status_code=500)
