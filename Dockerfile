# syntax=docker/dockerfile:1
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Usuario no-root (buena práctica)
RUN useradd -m appuser
WORKDIR /app

# --- Capa de deps (mejor cacheo) ---
# Copia solo metadatos del paquete y el código fuente para instalar
COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --upgrade pip && \
    pip install .

# --- Código y otros ficheros (tests, docs, etc.) ---
COPY . .

# Para que los imports "core.*" funcionen
ENV PYTHONPATH=/app/src

EXPOSE 8000

# Arranque (tu app es factoría)
CMD ["uvicorn", "infrastructure.server:build_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]

