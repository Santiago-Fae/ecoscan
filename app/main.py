import io
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageOps, UnidentifiedImageError
from pydantic import BaseModel

from . import db
from .classifier import analyze, load_models
from .recycling import MATERIALS, material_info

BASE = Path(__file__).parent
MAX_BYTES = 10 * 1024 * 1024


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    load_models()  # load YOLO + CLIP once, at startup
    yield


app = FastAPI(title="EcoScan - Recycling Identifier", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"materials": MATERIALS})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html", {"materials": MATERIALS})


@app.post("/api/analyze")
async def analyze_image(image: UploadFile = File(...), city: str = Form("")):
    if not (image.content_type or "").startswith("image/"):
        raise HTTPException(400, "Upload an image file (JPG, PNG, WEBP).")
    data = await image.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "Image is larger than 10 MB.")
    try:
        img = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(400, "Could not read the image.")
    result = await run_in_threadpool(analyze, img, city.strip() or None)
    await run_in_threadpool(db.record_analysis, result["items"])  # statistics only, no image
    return result


class Feedback(BaseModel):
    id: str
    correct: bool
    real_material: str | None = None
    city: str = ""


@app.post("/api/feedback")
async def feedback(f: Feedback):
    if not f.correct and f.real_material not in MATERIALS:
        raise HTTPException(422, "Provide the correct material.")
    final = await run_in_threadpool(db.record_feedback, f.id, f.correct, f.real_material)
    if final is None:
        raise HTTPException(409, "Detection does not exist or was already rated.")
    return {"ok": True, "material": material_info(final, f.city.strip() or None)}


@app.get("/api/stats")
async def stats():
    return await run_in_threadpool(db.stats)
