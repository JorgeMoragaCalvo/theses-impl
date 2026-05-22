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

COPY backend/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Runtime stage ---
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

LABEL org.opencontainers.image.title="Backend" \
      org.opencontainers.image.description="FastAPI service for AI Tutoring System" \
      org.opencontainers.image.version="1.6.4"

# LABEL maintainer="AI Tutoring System"

# Install runtime-only OS dependencies and create a non-root user
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 fonts-dejavu-core && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd --gid 1000 appuser && \
    useradd  --uid 1000 --gid appuser --shell /usr/sbin/nologin --create-home appuser

WORKDIR /app/backend

# Copy pre-built Python packages from the builder stage
COPY --from=builder /install /usr/local

# Copy application code, config, and data
COPY backend/app/  ./app/
COPY backend/init_db.py ./
COPY backend/gunicorn.conf.py ./
COPY data/ /app/data/

RUN chown -R appuser:appuser /app

USER appuser

# Pre-build matplotlib font cache so the first plot request isn't slow
RUN python -c "import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; plt.figure(); plt.plot([0,1],[0,1]); plt.close('all')"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
