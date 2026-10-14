"""Open-source AI pipeline:

1. YOLO11 (Ultralytics) locates the objects in the image.
2. CLIP ViT-L/14 (OpenAI, MIT) classifies the *material* of each crop (zero-shot).
3. If YOLO finds nothing usable (cans, cardboard, newspapers...), CLIP analyzes the whole image.
"""
import base64
import io
import os
from dataclasses import dataclass
from functools import lru_cache

import torch
from PIL import Image, ImageDraw, ImageFont

from .recycling import CONSIDER_COCO, NEGATIVE_PROMPTS, PROMPTS, material_info

YOLO_MODEL = os.getenv("YOLO_MODEL", "yolo11m.pt")
CLIP_MODEL = os.getenv("CLIP_MODEL", "ViT-L/14")  # lighter alternative: ViT-B/16
YOLO_CONF = float(os.getenv("YOLO_CONF", "0.25"))
MIN_MATERIAL_PROB = float(os.getenv("MIN_MATERIAL_PROB", "0.45"))
UNCERTAIN_BELOW = 0.70  # below this confidence, the user is asked to clarify
ALT_MIN_PROB = 0.10  # minimum probability to list an alternative material
MAX_OBJECTS = 8
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


@dataclass
class Models:
    yolo: object
    clip: object
    preprocess: object
    text: torch.Tensor  # (n_prompts, dim), normalized
    labels: list  # material key (or None for negative prompts) of each prompt, aligned with `text`


@lru_cache(maxsize=1)
def load_models() -> Models:
    import clip  # lazy import
    from ultralytics import YOLO

    clip_model, preprocess = clip.load(CLIP_MODEL, device=DEVICE)
    clip_model.eval()

    # One vector per prompt; probabilities are summed per material in classify_material.
    vectors, labels = [], []
    with torch.no_grad():
        for key, prompts in [*PROMPTS.items(), (None, NEGATIVE_PROMPTS)]:
            tokens = clip.tokenize([f"a photo of {p}" for p in prompts]).to(DEVICE)
            feats = clip_model.encode_text(tokens).float()
            vectors.append(feats / feats.norm(dim=-1, keepdim=True))
            labels += [key] * len(prompts)
    return Models(YOLO(YOLO_MODEL), clip_model, preprocess, torch.cat(vectors), labels)


def classify_material(models: Models, image: Image.Image) -> tuple[str | None, float, list]:
    """Return (material, probability, ranking). material is None if a negative label wins.
    `ranking` lists (material, prob) for the real materials, most likely first."""
    with torch.no_grad():
        x = models.preprocess(image).unsqueeze(0).to(DEVICE)
        feats = models.clip.encode_image(x).float()
        feats = feats / feats.norm(dim=-1, keepdim=True)
        probs = (100.0 * feats @ models.text.T).softmax(-1)[0]
    totals: dict = {}
    for key, p in zip(models.labels, probs.tolist()):
        totals[key] = totals.get(key, 0.0) + p
    best = max(totals, key=totals.get)
    ranking = sorted(((k, v) for k, v in totals.items() if k is not None), key=lambda kv: -kv[1])
    return best, totals[best], ranking


def _crop(image: Image.Image, xyxy, pad=0.08) -> Image.Image:
    x1, y1, x2, y2 = xyxy
    w, h = x2 - x1, y2 - y1
    box = (max(0, x1 - w * pad), max(0, y1 - h * pad), min(image.width, x2 + w * pad), min(image.height, y2 + h * pad))
    return image.crop(tuple(int(v) for v in box))


def _annotate(image: Image.Image, items: list) -> str:
    img = image.copy()
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=max(14, img.width // 40))
    for it in items:
        if it["box"] is None:
            continue
        color = it["material"]["hex"]
        draw.rectangle(it["box"], outline=color, width=max(3, img.width // 200))
        label = f'{it["material"]["name"]} {round(it["confidence"] * 100)}%'
        tb = draw.textbbox((it["box"][0], it["box"][1]), label, font=font)
        draw.rectangle(tb, fill=color)
        draw.text((tb[0], tb[1]), label, fill="white", font=font)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=88)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def analyze(image: Image.Image, city: str | None = None) -> dict:
    models = load_models()
    detections = models.yolo.predict(image, conf=YOLO_CONF, verbose=False)[0]

    candidates = []  # (box, yolo_class, yolo_conf)
    for b in detections.boxes:
        yolo_class = detections.names[int(b.cls)]
        if yolo_class not in CONSIDER_COCO:
            continue
        candidates.append(([float(v) for v in b.xyxy[0]], yolo_class, float(b.conf)))
    candidates = sorted(candidates, key=lambda c: -c[2])[:MAX_OBJECTS]

    best: dict[str, dict] = {}  # material -> best occurrence

    def consider(box, detected_as, crop, min_prob=MIN_MATERIAL_PROB):
        material, prob, ranking = classify_material(models, crop)
        if material is None or prob < min_prob:
            return
        if material not in best or prob > best[material]["confidence"]:
            # Plausible alternatives: used by the clarification question
            alternatives = [
                {**material_info(k, city), "confidence": round(v, 3)}
                for k, v in ranking[:3] if k != material and v >= ALT_MIN_PROB
            ]
            best[material] = {
                "detected_as": detected_as,
                "confidence": round(prob, 3),
                "uncertain": prob < UNCERTAIN_BELOW or bool(alternatives and alternatives[0]["confidence"] >= 0.25),
                "alternatives": alternatives,
                "box": [int(v) for v in box] if box else None,
                "material": material_info(material, city),
            }

    for box, yolo_class, _ in candidates:
        consider(box, yolo_class, _crop(image, box))

    # Whole image: covers objects YOLO (COCO) does not know (cans, cardboard, newspapers...).
    # With no usable crops it accepts lower confidence; with crops, only if quite confident.
    consider(None, "whole image", image, min_prob=0.6 if best else 0.4)

    items = sorted(best.values(), key=lambda i: -i["confidence"])
    return {
        "found": bool(items),
        "items": items,
        "annotated_image": _annotate(image, items),
    }
