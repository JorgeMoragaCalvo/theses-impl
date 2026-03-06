# ============================================================
# Backend – multi-stage production image
# ============================================================

# --- Build stage ---
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /tmp

# Install build-only dependencies (compiled wheels for psycopg2, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Runtime stage ---
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

LABEL org.opencontainers.image.title="Backend" \
      org.opencontainers.image.description="FastAPI service for AI Tutoring System" \
      org.opencontainers.image.version="1.6.4" \

# LABEL maintainer="AI Tutoring System"

# Install runtime-only OS dependencies and create a non-root user
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd --gid 1000 appuser && \
    useradd  --uid 1000 --gid appuser --shell /usr/sbin/nologin --create-home appuser

WORKDIR /app/backend

# Copy pre-built Python packages from the builder stage
COPY --from=builder /install /usr/local

# Copy application code and data
COPY backend/app/  ./app/
COPY backend/init_db.py ./
COPY data/ /app/data/

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
