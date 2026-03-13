from enum import Enum


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
    NOVICE = "novice"           # 0.0 - 0.30
    DEVELOPING = "developing"   # 0.30 - 0.60
    PROFICIENT = "proficient"   # 0.60 - 0.85
    MASTERED = "mastered"       # 0.85+


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
