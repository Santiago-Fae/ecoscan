<div align="center">

# ♻️ EcoScan

**Snap a photo. Find out what it's made of. Learn where to recycle it.**

An image-based recycling assistant powered by open-source computer vision (YOLO + CLIP), with a public statistics dashboard.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![YOLO11](https://img.shields.io/badge/YOLO11-Ultralytics-111F68)
![CLIP](https://img.shields.io/badge/CLIP-ViT--L%2F14-412991)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![Open Source AI](https://img.shields.io/badge/AI-100%25%20open%20source-43a047)

<img src="docs/screenshots/home.jpg" alt="EcoScan home page" width="720">

</div>

---

## ✨ Features

- 🔍 **Material identification from a photo:** plastic, glass, metal, paper/cardboard, electronics, organic waste and ceramics.
- 🗑️ **Actionable guidance:** bin color, how to prepare the item and where to drop it off, with a map search for your city.
- 🤔 **Clarification questions:** when the model is unsure, it asks *"Which of these is your item?"* instead of guessing.
- 👍 **User feedback:** every answer can be confirmed or corrected, which feeds the accuracy statistics.
- 📊 **Public dashboard:** see what users have identified (e.g. *"10 items were glass"*). **Only statistics are stored, never photos.**
- 🌱 **Educational page** about why recycling matters and how to sort waste.

<div align="center">
<img src="docs/screenshots/result.jpg" alt="Analysis result" width="48%">
<img src="docs/screenshots/dashboard.jpg" alt="Statistics dashboard" width="48%">
</div>

## 🧠 How it works

Off-the-shelf detectors (COCO) only know *"bottle"*, not *"glass bottle"* vs *"plastic bottle"*, and no ready-made
waste model was accurate enough. EcoScan combines two open-source models instead:

```mermaid
flowchart LR
    A[📷 Photo] --> B[YOLO11m<br/>locates objects]
    B -->|crop of each object| C[CLIP ViT-L/14<br/>zero-shot material]
    A -->|whole image fallback| C
    C --> D{Confident?}
    D -->|yes| E[Material + bin + drop-off]
    D -->|no| F[Ask the user:<br/>'Which one is it?']
    F --> E
    E --> G[(SQLite<br/>stats only)]
    G --> H[📊 Dashboard]
```

1. **YOLO11** (Ultralytics) finds the objects and crops them.
2. **CLIP ViT-L/14** (OpenAI, MIT) scores each crop against text descriptions such as *"a glass bottle"* or *"an aluminum can"*. Probabilities from several phrases are summed per material.
3. If YOLO finds nothing usable (cans, cardboard, newspapers...), CLIP analyzes the **whole image**.
4. Low confidence, or a close second candidate, triggers the **clarification question**.

On 21 test images from Wikimedia Commons, **19 were classified correctly**. The two misses were ambiguous photos
(bales of PET bottles tied with wire). Clear plastic vs. glass is the most common confusion.

## 🚀 Quick start

Requires **Python 3.10+** and **git** (to install the CLIP package).

```bash
git clone https://github.com/<your-user>/ecoscan.git
cd ecoscan

python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt

uvicorn app.main:app
```

Open **http://127.0.0.1:8000**.

> On the first run the model weights are downloaded automatically (YOLO11m ≈ 40 MB, CLIP ViT-L/14 ≈ 900 MB),
> so startup takes a while. Later runs start much faster.

## 🔌 API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web app |
| `GET` | `/dashboard` | Public statistics dashboard |
| `POST` | `/api/analyze` | `multipart/form-data` with `image` (required) and `city` (optional). Returns the detected items, alternatives, and an annotated image |
| `POST` | `/api/feedback` | JSON `{ "id", "correct", "real_material?", "city?" }`. One answer per detection |
| `GET` | `/api/stats` | Aggregated statistics as JSON |

<details>
<summary>Example response of <code>/api/analyze</code></summary>

```json
{
  "found": true,
  "items": [
    {
      "id": "9f2c…",
      "detected_as": "bottle",
      "confidence": 0.956,
      "uncertain": false,
      "alternatives": [],
      "box": [120, 40, 410, 600],
      "material": {
        "key": "glass",
        "name": "Glass",
        "bin_color": "Green",
        "recyclable": true,
        "how_to": "Rinse it and drop it off whole…",
        "drop_off": ["Green selective-collection bin", "Recycling center"],
        "map_url": "https://www.google.com/maps/search/glass+recycling+drop-off+Curitiba"
      }
    }
  ],
  "annotated_image": "data:image/jpeg;base64,…"
}
```

</details>

## ⚙️ Configuration

Environment variables:

| Variable | Default | Description |
|---|---|---|
| `YOLO_MODEL` | `yolo11m.pt` | Any YOLO weights (e.g. `yolo11l.pt`, or a model trained on waste) |
| `CLIP_MODEL` | `ViT-L/14` | Use `ViT-B/16` for lower memory/CPU usage |
| `YOLO_CONF` | `0.25` | Minimum confidence for object detections |
| `MIN_MATERIAL_PROB` | `0.45` | Minimum confidence for the material |
| `DB_PATH` | `data/ecoscan.db` | SQLite file for statistics |

To add materials or tune the classification, edit `MATERIALS` and `PROMPTS` in [`app/recycling.py`](app/recycling.py).

## 🗂️ Project structure

```
app/
├── main.py          # FastAPI routes
├── classifier.py    # YOLO + CLIP pipeline
├── recycling.py     # Materials, bin colors, CLIP prompts
├── db.py            # SQLite statistics (no images)
├── templates/       # index.html, dashboard.html (Jinja2)
└── static/          # CSS and vanilla JS
```

## 🔒 Privacy

Uploaded images are processed in memory and **never written to disk**. The database only stores the predicted
material, confidence, and the optional user feedback.

## ⚠️ Limitations

- Drop-off locations are generic guidance plus a map search link. For real addresses, integrate your municipality's recycling-point data (or OpenStreetMap's `amenity=recycling`).
- Bin colors follow Brazil's CONAMA color code, and collection rules vary by municipality.
- The dashboard and feedback endpoint are public and unauthenticated; add rate limiting before exposing them to the internet.

## 🛣️ Roadmap

- [ ] Real recycling points on a map (OpenStreetMap / Overpass API)
- [ ] Camera capture on mobile
- [ ] More materials (batteries, light bulbs, cooking oil, textiles, Tetra Pak)
- [ ] Fine-tuned model on TACO / TrashNet
- [ ] Docker image
- [ ] Automated tests with a reference image set

## 📄 License & credits

Built with [FastAPI](https://fastapi.tiangolo.com/), [Ultralytics YOLO](https://github.com/ultralytics/ultralytics)
and [OpenAI CLIP](https://github.com/openai/CLIP).

> **License note:** Ultralytics is licensed under **AGPL-3.0**, which applies if you run a modified version as a
> network service. Choose a license for this repository accordingly (AGPL-3.0 is the straightforward option).
