from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from PIL import Image
import io
import base64

app = FastAPI()

# Allow CORS (required if JS runs on different domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/convert/", response_class=HTMLResponse)
async def convert(file: UploadFile = File(...), conversion: str = Form(...)):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Dummy transformation: convert to grayscale
        image = image.convert("L").convert("RGB")

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"""
        <html><body>
            <img src="data:image/jpeg;base64,{img_str}" />
        </body></html>
        """
    except Exception as e:
        return HTMLResponse(f"<h2>Error: {str(e)}</h2>", status_code=500)
