# syntax=docker/dockerfile:1

# ---------- Stage 1: build the Python environment ----------
FROM python:3.12-slim-bookworm AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# git is only needed to install the CLIP package from GitHub (not shipped in the final image)
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# CPU-only PyTorch: far smaller than the default CUDA build
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
# Swap OpenCV for its headless build: no GUI libraries are needed in a server container
RUN pip install -r requirements.txt \
    && pip uninstall -y opencv-python \
    && pip install opencv-python-headless


# ---------- Stage 2: runtime image ----------
FROM python:3.12-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 1000 app \
    && mkdir -p /app /models /data \
    && chown -R app:app /app /models /data

COPY --from=builder /opt/venv /opt/venv

ARG CLIP_MODEL="ViT-L/14"
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOME=/home/app \
    YOLO_CONFIG_DIR=/home/app/.config/Ultralytics \
    YOLO_AUTOINSTALL=false \
    YOLO_MODEL=/models/yolo11m.pt \
    CLIP_MODEL=${CLIP_MODEL} \
    DB_PATH=/data/ecoscan.db

USER app

# Bake the open-source model weights into the image so the container starts offline and fast.
# YOLO downloads into the current directory (/models); CLIP caches under ~/.cache/clip.
WORKDIR /models
RUN python -c "import os, clip; clip.load(os.environ['CLIP_MODEL'], device='cpu')" \
    && python -c "from ultralytics import YOLO; YOLO('yolo11m.pt')"

WORKDIR /app
COPY --chown=app:app app ./app

VOLUME /data
EXPOSE 8000

# Models are loaded at startup, so give the app time before the first check
HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=4)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
