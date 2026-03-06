# ============================================================
# Frontend – multi-stage production image
# ============================================================

# --- Build stage ---
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /tmp

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dit --prefix=/install -r requirements.txt
# pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Runtime stage ---
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

LABEL maintainer="AI Tutoring System"

RUN groupadd --gid 1000 appuser && \
    useradd  --uid 1000 --gid appuser --shell /usr/sbin/nologin --create-home appuser

WORKDIR /app/frontend

# Copy pre-built Python packages from the builder stage
COPY --from=builder /install /usr/local

# Copy frontend application code
COPY frontend/ .

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"

CMD ["streamlit", "run", "app.py", "--server.port=${PORT:-8501}", "--server.address=0.0.0.0", "--server.headless=true"]
