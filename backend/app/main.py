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

# Student endpoints
@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    """Create a new student profile."""
    # Check if the email already exists
    existing_student = db.query(Student).filter(Student.email == student_data.email).first()
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with this email already exists"
        )

    new_student = Student(
        name=student_data.name,
        email=str(student_data.email),
        knowledge_levels=student_data.knowledge_levels or {
            "operations_research": "beginner",
            "mathematical_modeling": "beginner",
            "linear_programming": "beginner",
            "integer_programming": "beginner",
            "nonlinear_programming": "beginner"
        },
        preferences=student_data.preferences or {}
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    logger.info(f"Created new student: {new_student.id} - {new_student.email}")
    return new_student

@app.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, db: Session = Depends(get_db)):
    """Get the student profile by ID"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    return student

@app.put("/students/{student_id}", response_model=StudentResponse)
async def update_student(student_id: int, student_data: StudentUpdate, db: Session = Depends(get_db)):
    """Update student profile"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    if student_data.name is not None:
        student.name = student_data.name
    if student_data.email is not None:
        student.email = str(student_data.email)
    if student_data.knowledge_levels is not None:
        student.knowledge_level = student_data.knowledge_levels
    if student_data.preferences is not None:
        student.preferences = student_data.preferences

    db.commit()
    db.refresh(student)

    logger.info(f"Updated student: {student_id}")
    return student

@app.get("/students", response_model=List[StudentResponse])
async def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all students"""
    students = db.query(Student).offset(skip).limit(limit).all()
    return students

# Chat endpoint (placeholder - will be implemented with agents)
@app.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest, db: Session = Depends(get_db)):
    """
    Send a message and get the AI tutor response.
    This is a placeholder that will be replaced with actual agent logic.
    """
    # Verify student exists
    student = db.query(Student).filter(Student.id == chat_request.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Get or create conversation
    conversation = None
    if chat_request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == chat_request.conversation_id,
            Conversation.is_active == 1
        ).first()

    if not conversation:
        # Create the new conversation
        conversation = Conversation(
            student_id=chat_request.student_id,
            topic=chat_request.topic,
            is_active=1
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=chat_request.message
    )
    db.add(user_message)
    db.commit()

    try:
        # Get LP agent
        lp_agent = get_linear_programming_agent()

        # Get conversation service
        conversation_service = get_conversation_service(db)

        # Retrieve conversation history (last 10 messages)
        conversation_history = conversation_service.get_conversation_history(
            conversation_id=conversation.id
        )

        # Get student context
        context = conversation_service.get_conversation_context(
            conversation_id=conversation.id,
            student_id=chat_request.student_id,
            topic="linear_programming"
        )

        # Generate AI response
        response_text = lp_agent.generate_response(
            user_message=chat_request.message,
            conversation_history=conversation_history,
            context=context
        )
        agent_type = lp_agent.agent_type

        logger.info(f"Generated response for student {chat_request.student_id}: {len(response_text)} chars")
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        response_text = (
            "I apologize, but I encountered an error processing your request. "
            "Please try again or rephrase your question."
        )
        agent_type = "error"

    # Save the assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text,
        agent_type=agent_type
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    return ChatResponse(
        conversation_id=conversation.id,
        message_id=assistant_message.id,
        response=response_text,
        agent_type=agent_type,
        topic=chat_request.topic,
        timestamp=assistant_message.timestamp
    )

# Conversation endpoints
@app.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Get conversation by ID with all messages"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get all messages in conversation
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.timestamp).all()

    # return ConversationResponse(
    #     id=conversation.id,
    #     student_id=conversation.student_id,
    #     topic=conversation.topic,
    #     started_at=conversation.started_at,
    #     ended_at=conversation.ended_at,
    #     is_active=bool(conversation.is_active),
    #     messages=[MessageResponse.from_orm(msg) for msg in messages],
    #     metadata=conversation.metadata
    # )

    conv = ConversationResponse.model_validate(conversation)
    conv.messages = [MessageResponse.model_validate(msg) for msg in messages]
    return conv

@app.get("/students/{student_id}/conversations", response_model=List[ConversationResponse])
async def get_student_conversations(student_id: int, db: Session = Depends(get_db)):
    """Get all conversations for a student"""
    conversations = db.query(Conversation).filter(
        Conversation.student_id == student_id
    ).order_by(Conversation.started_at.desc()).all()

    return [
        ConversationResponse(
            id=conv.id,
            student_id=conv.student_id,
            topic=conv.topic,
            started_at=conv.started_at,
            ended_at=conv.ended_at,
            is_active=bool(conv.is_active),
            metadata=conv.metadata
        )
        for conv in conversations
    ]