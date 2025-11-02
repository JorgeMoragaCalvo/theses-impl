from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from contextlib import asynccontextmanager
import logging

from .config import settings
from .database import get_db, init_db, Student, Conversation, Message, Assessment, Feedback
from .models import (
    HealthResponse,
    StudentCreate,
    StudentResponse,
    StudentUpdate,
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    MessageResponse,
    FeedbackResponse,
    FeedbackCreate,
    ProgressResponse,
)
from .agents.linear_programming_agent import get_linear_programming_agent
from .services.conversation_service import get_conversation_service

"""
FastAPI main application entry point.
AI Tutoring System for Optimization Methods.
"""

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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

    yield

    # Shutdown
    logger.info("Shutting down AI Tutoring System...")

# Create FastAPI app
app = FastAPI(
    title="AI Tutoring System for Optimization Methods",
    description="Backend API for personalized AI tutoring in optimization methods.",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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