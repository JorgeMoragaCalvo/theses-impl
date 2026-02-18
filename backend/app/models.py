from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr, Field

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


class MasteryLevel(str, Enum):
    """Mastery level for a concept based on a mastery score."""
    NOT_STARTED = "not_started"
    NOVICE = "novice"
    DEVELOPING = "developing"
    PROFICIENT = "proficient"
    MASTERED = "mastered"


class EventCategory(str, Enum):
    """Category of activity event for analytics."""
    PAGE_VISIT = "page_visit"
    PAGE_EXIT = "page_exit"
    WIDGET_INTERACTION = "widget_interaction"
    CHAT_MESSAGE = "chat_message"
    ASSESSMENT_GENERATE = "assessment_generate"
    ASSESSMENT_SUBMIT = "assessment_submit"
    TOPIC_CHANGE = "topic_change"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    IDLE_START = "idle_start"
    IDLE_END = "idle_end"


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


class ExerciseAssessmentGenerate(BaseModel):
    """Request a model for generating assessment from a pre-built exercise."""
    exercise_id: str = Field(..., min_length=1, description="Exercise ID (e.g., 'mm_01')")
    mode: str = Field(
        default="practice",
        pattern="^(practice|similar)$",
        description="'practice' for original exercise, 'similar' for LLM-generated variation"
    )


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


class RegistrationPendingResponse(BaseModel):
    """Response model for registration pending admin approval."""
    status: str = "pending_approval"
    message: str
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


# Competency Tracking
class ConceptCompetencyResponse(BaseModel):
    """Response for a single concept's mastery."""
    concept_id: str
    concept_name: str
    mastery_level: str
    mastery_score: float
    attempts_count: int
    correct_count: int | None = None
    last_attempt_at: datetime | None = None

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Custom validation to handle enum conversion."""
        if hasattr(obj, '__dict__'):
            data = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
            if 'mastery_level' in data and hasattr(data['mastery_level'], 'value'):
                data['mastery_level'] = data['mastery_level'].value
            if 'topic' in data and hasattr(data['topic'], 'value'):
                data['topic'] = data['topic'].value
            return super().model_validate(data, **kwargs)
        return super().model_validate(obj, **kwargs)


class StudentCompetenciesResponse(BaseModel):
    """Response for all competencies of a student in a topic."""
    student_id: int
    topic: str
    competencies: list[ConceptCompetencyResponse]


class MasterySummaryResponse(BaseModel):
    """Response for mastery summary of a student in a topic."""
    student_id: int
    topic: str
    total_concepts: int
    level_counts: dict[str, int]
    average_mastery_score: float
    concepts: list[dict[str, Any]]


class RecommendedConceptResponse(BaseModel):
    """A single concept recommendation."""
    concept_id: str
    concept_name: str
    bloom_level: str
    current_mastery_score: float
    current_mastery_level: str
    prerequisites: list[str]


class RecommendedConceptsResponse(BaseModel):
    """Response for recommended concepts for a student."""
    student_id: int
    topic: str
    recommendations: list[RecommendedConceptResponse]


# Analytics Models
class ActivityEventCreate(BaseModel):
    """Request model for recording a single activity event."""
    session_id: str = Field(..., min_length=1, max_length=255)
    event_category: EventCategory
    event_action: str = Field(..., min_length=1, max_length=255)
    page_name: str | None = None
    topic: str | None = None
    duration_seconds: float | None = None
    extra_data: dict[str, Any] | None = None


class ActivityEventBatchCreate(BaseModel):
    """Request a model for recording a batch of activity events."""
    events: list[ActivityEventCreate] = Field(..., min_length=1, max_length=50)


class DailyActiveUsersResponse(BaseModel):
    """DAU over a date range."""
    dates: list[str]
    counts: list[int]


class SessionDurationResponse(BaseModel):
    """Average session duration by day."""
    dates: list[str]
    avg_duration_minutes: list[float]


class PeakUsageResponse(BaseModel):
    """Events grouped by hour of the day."""
    hours: list[int]
    event_counts: list[int]


class PagePopularityResponse(BaseModel):
    """Page visit counts and average duration."""
    pages: list[str]
    visit_counts: list[int]
    avg_duration_seconds: list[float]


class TopicPopularityResponse(BaseModel):
    """Topic interaction counts from analytics events."""
    topics: list[str]
    interaction_counts: list[int]


class UserEngagementResponse(BaseModel):
    """User engagement summary metrics."""
    total_events: int
    unique_sessions: int
    avg_events_per_session: float
    avg_session_duration_minutes: float
    total_chat_messages: int
    total_assessments_generated: int
    total_assessments_submitted: int


class AnalyticsSummaryResponse(BaseModel):
    """Combined analytics summary for the admin dashboard."""
    dau: DailyActiveUsersResponse
    session_duration: SessionDurationResponse
    peak_usage: PeakUsageResponse
    page_popularity: PagePopularityResponse
    topic_popularity: TopicPopularityResponse
    engagement: UserEngagementResponse
