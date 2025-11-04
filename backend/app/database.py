from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timezone
from typing import Generator
import enum

from .config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Create the SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the Base class for models
Base = declarative_base()

# Enums
class KnowledgeLevel(str, enum.Enum):
    """Student knowledge level for each topic."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class Topic(str, enum.Enum):
    """Optimization method topics."""
    OPERATIONS_RESEARCH = "operations_research"
    MATHEMATICAL_MODELING = "mathematical_modeling"
    LINEAR_PROGRAMMING = "linear_programming"
    INTEGER_PROGRAMMING = "integer_programming"
    NONLINEAR_PROGRAMMING = "nonlinear_programming"

class Student(Base):
    """Student profile model."""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    create_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    # Knowledge levels for each topic (stored as JSON)
    knowledge_levels = Column(JSON, default={
        "operations_research": "beginner",
        "mathematical_modeling": "beginner",
        "linear_programming": "beginner",
        "integer_programming": "beginner",
        "nonlinear_programming": "beginner"
    })
    # Learning preferences and metadata
    preferences = Column(JSON, default={})

class Conversation(Base):
    """Conversation session model."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False, index=True)
    topic = Column(Enum(Topic), nullable=False)
    started_at = Column(DateTime, default=datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Integer, default=1) # 1=True, 0=False
    extra_data = Column(JSON, default={}) # Session metadata

class Message(Base):
    """Individual message in a conversation."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, nullable=False, index=True)
    role = Column(String(50), nullable=False) # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    # Agent information
    agent_type = Column(String(100), nullable=True) # Which the agent responded
    extra_data = Column(JSON, default={})

class Assessment(Base):
    """Student assessment and quiz results."""
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False, index=True)
    conversation_id = Column(Integer, nullable=True)
    topic = Column(Enum(Topic), nullable=False)

    # Assessment Content
    question = Column(Text, nullable=False)
    student_answer = Column(Text, nullable=True)
    correct_answer = Column(Text, nullable=True)

    #Grading
    score = Column(Float, nullable=True)
    max_score = Column(Float, default=7.0)
    feedback = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    submitted_at = Column(DateTime, nullable=True)
    graded_at = Column(DateTime, nullable=True)

    extra_data = Column(JSON, default={})

class Feedback(Base):
    """Student feedback on agent responses."""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, nullable=False, index=True)
    student_id = Column(Integer, nullable=False, index=True)

    # Feedback data
    rating = Column(Integer, nullable=True) # 1 - 5 scale
    is_helpful = Column(Integer, nullable=True) # 1=True, 0=False
    comment = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    extra_data = Column(JSON, default={})

# Database dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    """
    Create a database session and close it after use.
    Used as a dependency in FastAPI routes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database initialization
def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)

def drop_db() -> None:
    """Drop all database tables (use with caution)."""
    Base.metadata.drop_all(bind=engine)