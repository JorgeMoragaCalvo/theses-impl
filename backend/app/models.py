from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from typing import Any

"""
Pydantic models for API request/response validation.
"""

# Enums
class KnowledgeLevel(str, Enum):
    """Student knowledge level for each topic."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class Topic(str, Enum):
    """Optimization method topics."""
    OPERATIONS_RESEARCH = "operations_research"
    MATHEMATICAL_MODELING = "mathematical_modeling"
    LINEAR_PROGRAMMING = "linear_programming"
    INTEGER_PROGRAMMING = "integer_programming"
    NONLINEAR_PROGRAMMING = "nonlinear_programming"

class MessageRole(str, Enum):
    """Message role in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class UserRole(str, Enum):
    """User role for authorization."""
    USER = "user"
    ADMIN = "admin"

class GradingSource(str, Enum):
    """Source of assessment grading."""
    AUTO = "auto"
    ADMIN = "admin"

# Request Models
class StudentCreate(BaseModel):
    """Request the model for creating a new student."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    knowledge_levels: dict[str, str] | None = None
    preferences: dict[str, Any] | None = None

class StudentRegister(BaseModel):
    """Request model for user registration."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)

class StudentLogin(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str = Field(..., min_length=1)

class StudentUpdate(BaseModel):
    """Request model for updating student information."""
    name: str = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    knowledge_levels: dict[str, str] | None = None
    preferences: dict[str, Any] | None = None

class MessageCreate(BaseModel):
    """Request model for creating a new message."""
    conversation_id: int | None = None
    content: str = Field(..., min_length=1)
    topic: Topic | None = None

class FeedbackCreate(BaseModel):
    """Request the model for creating new feedback."""
    message_id: int
    rating: int | None = Field(None, ge=1, le=5)
    is_helpful: bool | None = None
    comment: str | None= None

class AssessmentGenerate(BaseModel):
    """Request the model for generating a new assessment."""
    topic: Topic
    difficulty: KnowledgeLevel | None = KnowledgeLevel.INTERMEDIATE
    conversation_id: int | None= None

class AssessmentAnswerSubmit(BaseModel):
    """Request model for submitting a student's answer to an assessment."""
    student_answer: str = Field(..., min_length=1)

class AssessmentGradeRequest(BaseModel):
    """Request model for manually grading an assessment."""
    score: float = Field(..., ge=0)
    max_score: float | None = Field(None, ge=0)
    feedback: str | None= None

# Response Models (data output. How the API responds)
class StudentResponse(BaseModel):
    """Response model for student data."""
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    knowledge_levels: dict[str, str]
    preferences: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Response model for authentication token."""
    access_token: str
    token_type: str = "bearer"
    user: StudentResponse

class MessageResponse(BaseModel):
    """Response model for message data."""
    id: int
    conversation_id: int
    role: str
    content: str
    timestamp: datetime
    agent_type: str | None = None
    extra_data: dict[str, Any]

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    """Response model for conversation data."""
    id: int
    student_id: int
    topic: str
    started_at: datetime
    ended_at: datetime | None = None
    is_active: bool
    messages: list[MessageResponse] | None = None
    extra_data: dict[str, Any]

    class Config:
        from_attributes = True

class AssessmentResponse(BaseModel):
    """Response model for assessment data."""
    id: int
    student_id: int
    conversation_id: int | None= None
    topic: str
    question: str
    student_answer: str | None = None
    correct_answer: str | None = None
    rubric: str | None = None
    score: float | None = None
    max_score: float
    feedback: str | None = None
    graded_by: str | None = None
    overridden_at: datetime | None = None
    created_at: datetime
    submitted_at: datetime | None = None
    graded_at: datetime | None = None
    extra_data: dict[str, Any]

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Custom validation to handle enum conversion."""
        if hasattr(obj, '__dict__'):
            data = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
            # Convert topic enum to string value if it's an enum
            if 'topic' in data and hasattr(data['topic'], 'value'):
                data['topic'] = data['topic'].value
            # Convert graded_by enum to string value if it's an enum
            if 'graded_by' in data and hasattr(data['graded_by'], 'value'):
                data['graded_by'] = data['graded_by'].value
            return super().model_validate(data, **kwargs)
        return super().model_validate(obj, **kwargs)

class FeedbackResponse(BaseModel):
    """Response model for feedback data."""
    id: int
    message_id: int
    student_id: int
    rating: int | None = None
    is_helpful: bool | None = None
    comment: str | None = None
    created_at: datetime
    extra_data: dict[str, Any]

    class Config:
        from_attributes = True

# Chat Models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1)
    conversation_id: int | None = None
    topic: Topic  # The required field - auto-detect feature will be implemented later

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    conversation_id: int
    message_id: int
    response: str
    agent_type: str
    topic: str | None = None
    timestamp: datetime

# Health Check
class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str
    version: str
    llm_provider: str
    database_connected: bool

# Progress Tracking
class ProgressResponse(BaseModel):
    """Response model for student progress."""
    student_id: int
    knowledge_levels: dict[str, str]
    total_conversations: int
    total_messages: int
    total_assessments: int
    average_score: float | None = None
    topics_covered: list[str]
    recent_activity: list[dict[str, Any]]
