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
from .i18n import COOKIE, LANG_NAMES, SUPPORTED, js_strings, normalize, resolve_lang, t
from .recycling import localized_materials, material_info

BASE = Path(__file__).parent
MAX_BYTES = 10 * 1024 * 1024
COOKIE_MAX_AGE = 60 * 60 * 24 * 365


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    load_models()  # load YOLO + CLIP once, at startup
    yield


app = FastAPI(title="EcoScan - Recycling Identifier", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")


def render(request: Request, template: str):
    """Render a page in the requested language; `?lang=xx` is remembered in a cookie."""
    lang = resolve_lang(request)
    context = {
        "lang": lang,
        "t": lambda key, **kw: t(lang, key, **kw),
        "materials": localized_materials(lang),
        "i18n": js_strings(lang),
        "languages": {code: LANG_NAMES[code] for code in SUPPORTED},
    }
    response = templates.TemplateResponse(request, template, context)
    if normalize(request.query_params.get("lang")):
        response.set_cookie(COOKIE, lang, max_age=COOKIE_MAX_AGE, samesite="lax")
    return response


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return render(request, "index.html")


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return render(request, "dashboard.html")


@app.post("/api/analyze")
async def analyze_image(request: Request, image: UploadFile = File(...), city: str = Form(""), lang: str = Form("")):
    lang = resolve_lang(request, lang)
    if not (image.content_type or "").startswith("image/"):
        raise HTTPException(400, t(lang, "err_not_image"))
    data = await image.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(413, t(lang, "err_too_large"))
    try:
        img = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(400, t(lang, "err_unreadable"))
    result = await run_in_threadpool(analyze, img, city.strip() or None, lang)
    await run_in_threadpool(db.record_analysis, result["items"])  # statistics only, no image
    return result


class Feedback(BaseModel):
    id: str
    correct: bool
    real_material: str | None = None
    city: str = ""
    lang: str = ""


@app.post("/api/feedback")
async def feedback(request: Request, f: Feedback):
    lang = resolve_lang(request, f.lang)
    if not f.correct and f.real_material not in localized_materials():
        raise HTTPException(422, t(lang, "err_need_material"))
    final = await run_in_threadpool(db.record_feedback, f.id, f.correct, f.real_material)
    if final is None:
        raise HTTPException(409, t(lang, "err_conflict"))
    return {"ok": True, "material": material_info(final, f.city.strip() or None, lang)}


@app.get("/api/stats")
async def stats():
    return await run_in_threadpool(db.stats)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
