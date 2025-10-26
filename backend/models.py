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

# Request Models
class StudentCreate(BaseModel):
    """Request model for creating a new student."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    knowledge_levels: Optional[Dict[str, str]] = None
    preferences: Optional[Dict[str, Any]] = None

class StudentUpdate(BaseModel):
    """Request model for updating student information."""
    name: str = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    knowledge_levels: Optional[Dict[str, str]] = None
    preferences: Optional[Dict[str, Any]] = None

class MessageCreate(BaseModel):
    """Request model for creating a new message."""
    conversation_id: Optional[int] = None
    student_id: int
    content: str = Field(..., min_length=1)
    topic: Optional[Topic] = None

class FeedbackCreate(BaseModel):
    """Request model for creating a new feedback."""
    message_id: int
    student_id: int
    rating: Optional[int] = Field(None, ge=1, le=5)
    is_helpful: Optional[bool] = None
    comment: Optional[str] = None

class AssessmentSubmit(BaseModel):
    """Request model for generating a new assessment."""
    student_id: int
    topic: Topic
    difficulty: Optional[KnowledgeLevel] = KnowledgeLevel.INTERMEDIATE

# Response Models
class StudentResponse(BaseModel):
    """Response model for student data."""
    id: int
    name: str
    email: str
    knowledge_levels: Dict[str, str]
    preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    """Response model for message data."""
    id: int
    conversation_id: int
    role: str
    content: str
    timestamp: datetime
    agent_type: Optional[str] = None
    metadata = Dict[str, Any]

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
    metadata: Dict[str, Any]

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
    metadata: Dict[str, Any]

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
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True

# Chat Models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    student_id: int
    message: str = Field(..., min_length=1)
    conversation_id: Optional[int] = None
    topic: Optional[Topic] = None

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    conversation_id: int
    message_id: int
    response: str
    agent_type: str
    topic: Optional[str] = None
    timestamp: datetime

# Health Check
class HealthCheckResponse(BaseModel):
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