import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal, get_db, init_db
from .models import HealthResponse
from .rate_limit import limiter, rate_limit_exceeded_handler
from .routers import (
    admin,
    analytics,
    assessments,
    auth,
    chat,
    competencies,
    exercises,
    feedback,
    reviews,
    students,
)
from .services.competency_service import get_competency_service

"""
FastAPI main application entry point.
AI Tutoring System for Optimization Methods.
"""

if settings.debug:
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
else:
    from pythonjsonlogger import json

    handler = logging.StreamHandler()
    handler.setFormatter(json.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level", "name": "logger"},
    ))
    logging.root.handlers = [handler]
    logging.root.setLevel(settings.log_level.upper())

logger = logging.getLogger(__name__)

# --- Sentry error tracking (opt-in via SENTRY_DSN) ---
if settings.sentry_dsn:
    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=0.0 if settings.debug else settings.sentry_traces_sample_rate,
        send_default_pii=False,
        environment="development" if settings.debug else "production",
        release=settings.version,
    )
    logger.info("Sentry initialized (environment=%s)", "development" if settings.debug else "production")


# Lifespan context manager
@asynccontextmanager
async def lifespan(_: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    logger.info("Starting AI Tutoring System...")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info(f"Model: {settings.current_model}")

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Seed concept hierarchy from taxonomy files
    try:
        seed_db = SessionLocal()
        try:
            competency_svc = get_competency_service(seed_db)
            inserted = competency_svc.seed_concept_hierarchy()
            if inserted > 0:
                logger.info(f"Concept hierarchy seeded: {inserted} new concepts")
            else:
                logger.info("Concept hierarchy already seeded")
        finally:
            seed_db.close()
    except Exception as e:
        logger.warning(f"Could not seed concept hierarchy: {e}")

    yield

    # Shutdown
    logger.info("Shutting down AI Tutoring System...")


# Create FastAPI app
app = FastAPI(
    title="AI Tutoring System for Optimization Methods",
    description="Backend API for personalized AI tutoring in optimization methods.",
    version=settings.version,
    debug=settings.debug,
    lifespan=lifespan
)

# Register rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Configure CORS
cors_origins = (
    [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
    if settings.cors_origins
    else ["*"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=600,
)

# Include routers
app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(chat.router)
app.include_router(assessments.router)
app.include_router(exercises.router)
app.include_router(competencies.router)
app.include_router(reviews.router)
app.include_router(feedback.router)
app.include_router(analytics.router)

# --- Prometheus metrics (opt-in via ENABLE_PROMETHEUS) ---
if settings.enable_prometheus:
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        excluded_handlers=["/health", "/metrics"],
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    ).instrument(app).expose(
        app, endpoint="/metrics", include_in_schema=False, should_gzip=True
    )
    logger.info("Prometheus metrics enabled at /metrics")


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    database_connected = False
    try:
        db.execute(text("SELECT 1"))
        database_connected = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")

    return HealthResponse(
        status="healthy" if database_connected else "degraded",
        version=settings.version,
        llm_provider=settings.llm_provider,
        database_connected=database_connected
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with AI information"""
    return {
        "message": "AI Tutoring System for Optimization Methods",
        "version": settings.version,
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug
    )
