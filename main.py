from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from PIL import Image
import io, base64
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

app = FastAPI()

# Allow CORS for browser-based frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files if needed
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 template rendering
templates = Jinja2Templates(directory="templates")

# Home route (serves index.html)
@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Convert uploaded image (dummy grayscale for now)
@app.post("/convert/", response_class=HTMLResponse)
async def convert(request: Request, file: UploadFile = File(...), conversion: str = Form(...)):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Dummy transformation: convert to grayscale
        image = image.convert("L").convert("RGB")

        # Encode processed image as base64
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        # Return an HTML fragment with the result
        return HTMLResponse(f"""
        <html><body>
            <img src="data:image/jpeg;base64,{img_str}" />
        </body></html>
        """)
    except Exception as e:
        return HTMLResponse(f"<h2>Error: {str(e)}</h2>", status_code=500)
