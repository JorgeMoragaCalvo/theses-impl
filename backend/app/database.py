import enum
from collections.abc import Generator
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from .config import settings

"""
Database configuration and session management for PostgreSQL.
"""

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_pre_ping=True, # sends a "ping" to check if the connection is still alive
    pool_size=5, # How many simultaneous connections to keep open with the database
    max_overflow=10 # How many additional connections to allow if the pool reaches its size
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


class UserRole(str, enum.Enum):
    """User role for authorization."""
    USER = "user"
    ADMIN = "admin"


class GradingSource(str, enum.Enum):
    """Source of assessment grading."""
    AUTO = "auto"
    ADMIN = "admin"


class MasteryLevel(str, enum.Enum):
    """Mastery level for a concept based on a mastery score."""
    NOT_STARTED = "not_started"
    NOVICE = "novice"           # 0.0 - 0.30
    DEVELOPING = "developing"   # 0.30 - 0.60
    PROFICIENT = "proficient"   # 0.60 - 0.85
    MASTERED = "mastered"       # 0.85+


# Database Models
class Student(Base):
    """Student profile model."""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
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
    # Extra data stores session metadata and adaptive learning tracking:
    # - strategies_used: list[str] - List of explanation strategies used in this conversation
    # - confusion_count: int - Number of times confusion was detected
    # - successful_strategies: dict - Strategies that resolved confusion (strategy -> success count)
    # - last_strategy: str - Most recently used strategy
    # - student_preferences: dict - Inferred student preferences from interaction patterns
    # Metadata
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
    # Extra data stores adaptive learning metadata:
    # - explanation_strategy: str - Strategy used for this response (e.g., "step-by-step", "example-based")
    # - confusion_detected: bool - Whether confusion was detected in the user message
    # - confusion_level: str - Level of confusion (none/low/medium/high)
    # - feedback_requested: bool - Whether agent requested understanding feedback
    # - contains_alternative: bool - Whether this is an alternative explanation
    # Metadata
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
    rubric = Column(Text, nullable=True)

    #Grading
    score = Column(Float, nullable=True)
    max_score = Column(Float, default=7.0)
    feedback = Column(Text, nullable=True)
    graded_by = Column(Enum(GradingSource), nullable=True)  # Tracks if auto-graded or manually graded
    overridden_at = Column(DateTime, nullable=True)  # When admin overrode the auto-grade

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    submitted_at = Column(DateTime, nullable=True)
    graded_at = Column(DateTime, nullable=True)

    # Metadata
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

    # Metadata
    extra_data = Column(JSON, default={})


class StudentCompetency(Base):
    """Tracks mastery of a specific concept for a student."""
    __tablename__ = "student_competencies"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False, index=True)
    topic = Column(Enum(Topic), nullable=False)
    concept_id = Column(String(255), nullable=False, index=True)
    concept_name = Column(String(255), nullable=False)
    mastery_level = Column(Enum(MasteryLevel), default=MasteryLevel.NOVICE, nullable=False)
    mastery_score = Column(Float, default=0.0, nullable=False)
    attempts_count = Column(Integer, default=0, nullable=False)
    correct_count = Column(Integer, default=0, nullable=False)
    last_attempt_at = Column(DateTime, nullable=True)
    last_correct_at = Column(DateTime, nullable=True)
    decay_factor = Column(Float, default=2.5)  # SM-2 ease factor, reserved for Phase 3
    next_review_at = Column(DateTime, nullable=True)
    extra_data = Column(JSON, default={})

    __table_args__ = (
        UniqueConstraint("student_id", "concept_id", name="uq_student_concept"),
    )


class ConceptHierarchy(Base):
    """Stores the concept taxonomy for each topic."""
    __tablename__ = "concept_hierarchy"

    id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(String(255), nullable=False, unique=True, index=True)
    concept_name = Column(String(255), nullable=False)
    topic = Column(Enum(Topic), nullable=False)
    parent_concept_id = Column(String(255), nullable=True)
    bloom_level = Column(String(50), nullable=False)
    prerequisites = Column(JSON, default=[])
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


# Database cleanup
def drop_db() -> None:
    """Drop all database tables (use with caution)."""
    Base.metadata.drop_all(bind=engine)
