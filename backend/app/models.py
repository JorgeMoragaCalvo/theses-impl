from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from enum import Enum

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

# Request Models
class StudentCreate(BaseModel):
    """Request the model for creating a new student."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    knowledge_levels: Optional[Dict[str, str]] = None
    preferences: Optional[Dict[str, Any]] = None

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
    email: Optional[EmailStr] = None
    knowledge_levels: Optional[Dict[str, str]] = None
    preferences: Optional[Dict[str, Any]] = None

class MessageCreate(BaseModel):
    """Request model for creating a new message."""
    conversation_id: Optional[int] = None
    content: str = Field(..., min_length=1)
    topic: Optional[Topic] = None

class FeedbackCreate(BaseModel):
    """Request the model for creating new feedback."""
    message_id: int
    rating: Optional[int] = Field(None, ge=1, le=5)
    is_helpful: Optional[bool] = None
    comment: Optional[str] = None

class AssessmentGenerate(BaseModel):
    """Request the model for generating a new assessment."""
    topic: Topic
    difficulty: Optional[KnowledgeLevel] = KnowledgeLevel.INTERMEDIATE
    conversation_id: Optional[int] = None

class AssessmentAnswerSubmit(BaseModel):
    """Request model for submitting a student's answer to an assessment."""
    student_answer: str = Field(..., min_length=1)

class AssessmentGradeRequest(BaseModel):
    """Request model for manually grading an assessment."""
    score: float = Field(..., ge=0)
    max_score: Optional[float] = Field(None, ge=0)
    feedback: Optional[str] = None

# Response Models
class StudentResponse(BaseModel):
    """Response model for student data."""
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    knowledge_levels: Dict[str, str]
    preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

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
    agent_type: Optional[str] = None
    extra_data: Dict[str, Any]

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    """Response model for conversation data."""
    id: int
    student_id: int
    topic: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    is_active: bool
    messages: Optional[List[MessageResponse]] = None
    extra_data: Dict[str, Any]

    class Config:
        from_attributes = True

class AssessmentResponse(BaseModel):
    """Response model for assessment data."""
    id: int
    student_id: int
    conversation_id: Optional[int] = None
    topic: str
    question: str
    student_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    score: Optional[float] = None
    max_score: float
    feedback: Optional[str] = None
    created_at: datetime
    submitted_at: Optional[datetime] = None
    graded_at: Optional[datetime] = None
    extra_data: Dict[str, Any]

    class Config:
        from_attributes = True

class FeedbackResponse(BaseModel):
    """Response model for feedback data."""
    id: int
    message_id: int
    student_id: int
    rating: Optional[int] = None
    is_helpful: Optional[bool] = None
    comment: Optional[str] = None
    created_at: datetime
    extra_data: Dict[str, Any]

    class Config:
        from_attributes = True

# Chat Models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1)
    conversation_id: Optional[int] = None
    topic: Topic  # The required field - auto-detect feature will be implemented later

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    conversation_id: int
    message_id: int
    response: str
    agent_type: str
    topic: Optional[str] = None
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
    knowledge_levels: Dict[str, str]
    total_conversations: int
    total_messages: int
    total_assessments: int
    average_score: Optional[float] = None
    topics_covered: List[str]
    recent_activity: List[Dict[str, Any]]