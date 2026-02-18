import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from .agents.integer_programming_agent import get_integer_programming_agent
from .agents.linear_programming_agent import get_linear_programming_agent
from .agents.mathematical_modeling_agent import get_mathematical_modeling_agent

# from .agents.nonlinear_programming_agent import get_nonlinear_programming_agent
from .agents.nlp_agent import get_nonlinear_programming_agent
from .agents.operations_research_agent import get_operations_research_agent
from .auth import (
    authenticate_user,
    create_access_token,
    get_current_admin_user,
    get_current_user,
    get_password_hash,
)
from .config import settings
from .database import (
    Assessment,
    Conversation,
    Feedback,
    GradingSource,
    Message,
    SessionLocal,
    Student,
    Topic,
    UserRole,
    get_db,
    init_db,
)
from .models import (
    ActivityEventBatchCreate,
    AssessmentAnswerSubmit,
    AssessmentGenerate,
    AssessmentGradeRequest,
    AssessmentResponse,
    ChatRequest,
    ChatResponse,
    ConceptCompetencyResponse,
    ConversationResponse,
    ExerciseAssessmentGenerate,
    FeedbackCreate,
    FeedbackResponse,
    HealthResponse,
    MasterySummaryResponse,
    MessageResponse,
    ProgressResponse,
    RecommendedConceptResponse,
    RecommendedConceptsResponse,
    RegistrationPendingResponse,
    StudentCompetenciesResponse,
    StudentCreate,
    StudentLogin,
    StudentRegister,
    StudentResponse,
    StudentUpdate,
    TokenResponse,
)
from .routers import admin
from .services.analytics_service import get_analytics_service
from .services.assessment_service import get_assessment_service
from .services.competency_service import get_competency_service
from .services.conversation_service import get_conversation_service
from .services.exercise_assessment_service import (
    get_exercise_assessment_service,
    get_exercise_registry,
)
from .services.exercise_progress_service import (
    compute_max_unlocked_rank,
    get_completed_exercise_ids,
    get_exercises_with_progress,
)
from .services.grading_service import get_grading_service

"""
FastAPI main application entry point.
AI Tutoring System for Optimization Methods.
"""

logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Agent Registry - Maps topic names to agent getter functions
AGENT_REGISTRY = {
    "operations_research": get_operations_research_agent,
    "linear_programming": get_linear_programming_agent,
    "mathematical_modeling": get_mathematical_modeling_agent,
    "nonlinear_programming": get_nonlinear_programming_agent,
    "integer_programming": get_integer_programming_agent
}


def _sanitize_log_value(value: str) -> str:
    """Sanitize log value to prevent log injection."""
    return str(value).replace("\r", "").replace("\n", "")

def get_agent_for_topic(topic: str):
    """
    Get the appropriate agent for a given topic.

    Args:
        topic: Topic string (e.g., "linear_programming", "mathematical_modeling")

    Returns:
        Agent instance for the specified topic
    """
    agent_getter = AGENT_REGISTRY.get(topic)
    safe_topic = _sanitize_log_value(topic)
    if agent_getter is None:
        logger.warning(f"No agent found for topic '{safe_topic}', falling back to linear programming agent")
        return get_linear_programming_agent()

    logger.info(f"Selected agent for topic: {safe_topic}")
    return agent_getter()

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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin.router)

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

# Authentication endpoints
# Allowed email domain for automatic activation
ALLOWED_EMAIL_DOMAIN = "usach.cl"

@app.post("/auth/register", response_model=TokenResponse | RegistrationPendingResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: StudentRegister, db: Session = Depends(get_db)):
    """Register a new user and return the JWT token."""
    # Check if email already exists
    existing_user = db.query(Student).filter(Student.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check email domain for automatic activation
    email_domain = str(user_data.email).split('@')[1].lower()
    is_allowed_domain = email_domain == ALLOWED_EMAIL_DOMAIN

    # Create a new student with a hashed password
    new_student = Student(
        name=user_data.name,
        email=str(user_data.email),
        password_hash=get_password_hash(user_data.password),
        role=UserRole.USER,  # Default role
        is_active=is_allowed_domain,  # Only allowed domain users are active immediately
        knowledge_levels={
            "operations_research": "beginner",
            "mathematical_modeling": "beginner",
            "linear_programming": "beginner",
            "integer_programming": "beginner",
            "nonlinear_programming": "beginner"
        },
        preferences={}
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    logger.info(f"New user registered: {new_student.id} - {new_student.email} (active: {is_allowed_domain})")

    # Return pending response for non-allowed domains
    if not is_allowed_domain:
        return RegistrationPendingResponse(
            status="pending_approval",
            message="Cuenta creada. Tu cuenta está pendiente de aprobación por un administrador debido al dominio de correo.",
            user=StudentResponse.model_validate(new_student)
        )

    # Create the access token for allowed domain users
    access_token = create_access_token(data={"sub": str(new_student.id)})

    return TokenResponse(
        access_token=access_token,
        user=StudentResponse.model_validate(new_student)
    )

@app.post("/auth/login", response_model=TokenResponse)
async def login(credentials: StudentLogin, db: Session = Depends(get_db)):
    """Login with email and password, return JWT token."""
    # Authenticate user
    student = authenticate_user(db, str(credentials.email), credentials.password)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login timestamp
    student.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(student)

    # Create the access token
    access_token = create_access_token(data={"sub": str(student.id)})

    logger.info(f"User logged in: {student.id} - {student.email}")

    return TokenResponse(
        access_token=access_token,
        # token_type="bearer",
        user=StudentResponse.model_validate(student)
    )

@app.get("/auth/me", response_model=StudentResponse)
async def get_me(current_user: Student = Depends(get_current_user)):
    """Get current authenticated user information."""
    return StudentResponse.model_validate(current_user)

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
async def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Get the student profile by ID. Requires authentication."""
    # Users can view their own profile, admins can view any profile
    if current_user.id != student_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this profile"
        )

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    return student

@app.put("/students/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Update student profile. Users can only update their own profile."""
    # Users can only update their own profile
    if current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this profile"
        )

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
        student.knowledge_levels = student_data.knowledge_levels
    if student_data.preferences is not None:
        student.preferences = student_data.preferences

    db.commit()
    db.refresh(student)

    safe_student_id = _sanitize_log_value(str(student_id))
    logger.info(f"Updated student: {safe_student_id}")
    return student

@app.get("/students", response_model=list[StudentResponse])
async def list_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    # current_admin: Student = Depends(get_current_admin_user)
):
    """List all students. Admin only."""
    students = db.query(Student).offset(skip).limit(limit).all()
    return students

# Chat endpoint (placeholder - will be implemented with agents)
@app.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """
    Send a message and get the AI tutor response.
    Requires authentication.
    """
    # Use authenticated user's ID instead of request data
    student_id = current_user.id

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
            student_id=student_id,
            topic=chat_request.topic,
            is_active=1
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Verify the conversation belongs to the authenticated user
    if conversation.student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )

    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=chat_request.message
    )
    db.add(user_message)
    db.commit()

    try:
        # Get the appropriate agent based on the topic
        topic_value = chat_request.topic.value  # Get string value from enum
        agent = get_agent_for_topic(topic_value)

        # Get conversation service
        conversation_service = get_conversation_service(db)

        # Retrieve conversation history (last 10 messages)
        conversation_history = conversation_service.get_conversation_history(
            conversation_id=conversation.id
        )

        # Get student context with the actual topic
        context = conversation_service.get_conversation_context(
            conversation_id=conversation.id,
            student_id=student_id,
            topic=topic_value
        )

        # Generate AI response using the selected agent
        response_text = agent.generate_response(
            user_message=chat_request.message,
            conversation_history=conversation_history,
            context=context
        )
        agent_type = agent.agent_type

        logger.info(f"Generated response for student {student_id} using {agent_type} agent: {len(response_text)} chars")
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
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Get conversation by ID with all messages. Requires authentication."""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Users can only view their own conversations
    if conversation.student_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this conversation"
        )

    # Get all messages in conversation
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.timestamp).all()

    conv = ConversationResponse.model_validate(conversation)
    conv.messages = [MessageResponse.model_validate(msg) for msg in messages]
    return conv

@app.get("/students/{student_id}/conversations", response_model=list[ConversationResponse])
async def get_student_conversations(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Get all conversations for a student. Requires authentication."""
    # Users can only view their own conversations, admins can view any
    if current_user.id != student_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these conversations"
        )

    conversations = db.query(Conversation).filter(
        Conversation.student_id == student_id
    ).order_by(Conversation.started_at.desc()).all()

    return [ConversationResponse.model_validate(conv) for conv in conversations]

# Feedback endpoint
@app.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Create feedback for a message. Requires authentication."""
    # Verify message exists
    message = db.query(Message).filter(Message.id == feedback_data.message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    # Create feedback (use authenticated user's ID)
    new_feedback = Feedback(
        message_id=feedback_data.message_id,
        student_id=current_user.id,
        rating=feedback_data.rating,
        is_helpful=1 if feedback_data.is_helpful else 0 if feedback_data.is_helpful is not None else None,
        comment=feedback_data.comment
    )

    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)

    safe_feedback = _sanitize_log_value(str(feedback_data.message_id))
    logger.info(f"Created feedback for message {safe_feedback}")

    return FeedbackResponse(
        id=new_feedback.id,
        message_id=new_feedback.message_id,
        student_id=new_feedback.student_id,
        rating=new_feedback.rating,
        is_helpful=bool(new_feedback.is_helpful) if new_feedback.is_helpful is not None else None,
        comment=new_feedback.comment,
        created_at=new_feedback.created_at,
        extra_data=new_feedback.extra_data,
    )

# Analytics event ingestion endpoint
@app.post("/analytics/events", status_code=status.HTTP_201_CREATED)
async def record_activity_events(
    batch: ActivityEventBatchCreate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Record a batch of activity events for the current user. Requires authentication."""
    analytics_service = get_analytics_service(db)
    count = analytics_service.record_events(current_user.id, batch.events)
    return {"recorded": count}

# Progress endpoint
@app.get("/students/{student_id}/progress", response_model=ProgressResponse)
async def get_student_progress(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Get comprehensive progress metrics for a student. Requires authentication."""
    # Users can only view their own progress, admins can view any
    if current_user.id != student_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this progress"
        )

    # Verify student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Get conversation service
    conversation_service = get_conversation_service(db)

    # Compute progress
    progress = conversation_service.compute_student_progress(student_id)

    safe_student_id = _sanitize_log_value(str(student_id))
    logger.info(f"Retrieved progress for student {safe_student_id}")
    return progress

# Assessment endpoints
@app.get("/students/{student_id}/assessments", response_model=list[AssessmentResponse])
async def get_student_assessments(
    student_id: int,
    topic: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Get all assessments for a student, optionally filtered by topic. Requires authentication."""
    # Users can only view their own assessments, admins can view any
    if current_user.id != student_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these assessments"
        )

    # Verify student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Build query
    query = db.query(Assessment).filter(Assessment.student_id == student_id)

    # Filter by topic if provided
    if topic:
        query = query.filter(Assessment.topic == topic)

    # Get assessments
    assessments = query.order_by(
        Assessment.created_at.desc()
    ).offset(skip).limit(limit).all()

    return [AssessmentResponse.model_validate(assessment) for assessment in assessments]

@app.get("/assessments/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Get a specific assessment by ID. Requires authentication."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )

    # Users can only view their own assessments, admins can view any
    if assessment.student_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this assessment"
        )

    return AssessmentResponse.model_validate(assessment)

@app.post("/assessments/generate", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def generate_assessment(
    assessment_data: AssessmentGenerate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Generate a new assessment for the authenticated student on a specific topic."""
    # Use authenticated user's ID instead of request data
    student_id = current_user.id

    # Verify conversation exists if provided and belongs to the user
    if assessment_data.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == assessment_data.conversation_id
        ).first()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        if conversation.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to use this conversation"
            )

    # Generate personalized assessment using LLM
    assessment_service = get_assessment_service(db)

    try:
        generated_assessment = assessment_service.generate_personalized_assessment(
            student_id=student_id,
            topic=assessment_data.topic,
            difficulty=str(assessment_data.difficulty.value),
            conversation_id=assessment_data.conversation_id
        )

        question = generated_assessment.get("question")
        correct_answer = generated_assessment.get("correct_answer")
        rubric = generated_assessment.get("rubric")
        metadata = generated_assessment.get("metadata", {})

        # Add difficulty to metadata
        metadata["difficulty"] = assessment_data.difficulty.value

    except Exception as e:
        logger.error(f"Error generating personalized assessment: {str(e)}")
        # Fallback to simple assessment
        question = f"Practice problem for {assessment_data.topic.value} at {assessment_data.difficulty.value} level"
        correct_answer = None
        rubric = None
        metadata = {"difficulty": assessment_data.difficulty.value, "generation_error": True}

    new_assessment = Assessment(
        student_id=student_id,
        conversation_id=assessment_data.conversation_id,
        topic=assessment_data.topic,
        question=question,
        correct_answer=correct_answer,
        rubric=rubric,
        max_score=7.0,  # Default max score
        extra_data=metadata
    )

    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)

    logger.info(f"Generated assessment {new_assessment.id} for student {student_id}")
    return AssessmentResponse.model_validate(new_assessment)


# ============================================================================
# EXERCISE ENDPOINTS
# ============================================================================

@app.get("/exercises")
async def list_exercises(topic: Topic | None = None):
    """
    List available exercises, optionally filtered by topic.

    Args:
        topic: Optional topic to filter exercises by
    """
    registry = get_exercise_registry()
    if topic:
        return registry.list_exercises_by_topic(topic)
    return registry.list_all_exercises()


@app.get("/exercises/progress")
async def list_exercises_with_progress(
    topic: Topic | None = None,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):
    """List exercises enriched with locked/completed status for the current student."""
    return get_exercises_with_progress(db, current_user.id, topic)


@app.get("/exercises/{exercise_id}")
async def get_exercise_preview(exercise_id: str):
    """Get exercise details (statement only, no solution)."""
    service = get_exercise_assessment_service()
    preview = service.get_exercise_preview(exercise_id)

    if preview is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise '{exercise_id}' not found"
        )

    return preview


@app.post("/assessments/generate/from-exercise", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def generate_assessment_from_exercise(
    request: ExerciseAssessmentGenerate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """
    Generate an assessment from a pre-built exercise.

    Modes:
    - practice: Use the exercise directly as the assessment
    - similar: Generate a similar problem using LLM
    """
    student_id = current_user.id

    # Get registry to determine topic from exercise
    registry = get_exercise_registry()
    topic = registry.get_topic_for_exercise(request.exercise_id)

    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise '{request.exercise_id}' not found"
        )

    # Gating: check if the exercise is locked for this student
    exercises = registry.list_exercises_by_topic(topic)
    target_exercise = next((ex for ex in exercises if ex["id"] == request.exercise_id), None)
    if target_exercise:
        target_rank = target_exercise.get("rank", 0)
        if target_rank > 0:
            completed_ids = get_completed_exercise_ids(db, student_id, topic)
            max_unlocked = compute_max_unlocked_rank(completed_ids, exercises)
            if target_rank > max_unlocked:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Exercise is locked. Complete exercises at the previous rank first.",
                )

    # Get the manager for this topic's exercises
    manager = registry.get_manager(topic)
    if manager is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Exercise manager for topic '{topic.value}' not available"
        )

    service = get_exercise_assessment_service()
    # Temporarily set the correct manager for the service
    original_manager = service.exercise_manager
    service.exercise_manager = manager

    try:
        generated = service.create_assessment(
            exercise_id=request.exercise_id,
            mode=request.mode
        )

        question = generated.get("question", "")
        correct_answer = generated.get("correct_answer", "")
        rubric = generated.get("rubric", "")
        metadata = generated.get("metadata", {})
        # Add a topic to metadata for reference
        metadata['topic'] = topic.value

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating exercise assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate assessment from exercise"
        )
    finally:
        # Restore the original manager
        service.exercise_manager = original_manager

    # Create an assessment in a database with an inferred topic
    new_assessment = Assessment(
        student_id=student_id,
        topic=topic,  # Dynamic topic from exercise
        question=question,
        correct_answer=correct_answer,
        rubric=rubric,
        max_score=7.0,
        extra_data=metadata
    )

    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)

    # Sanitize user-controlled values before logging to prevent log injection
    safe_exercise_id = str(request.exercise_id).replace("\r", "").replace("\n", "")
    safe_mode = str(request.mode).replace("\r", "").replace("\n", "")

    logger.info(
        f"Generated exercise assessment {new_assessment.id} for student {student_id} "
        f"(exercise: {safe_exercise_id}, mode: {safe_mode})"
    )
    return AssessmentResponse.model_validate(new_assessment)


@app.post("/assessments/{assessment_id}/submit", response_model=AssessmentResponse)
async def submit_assessment_answer(
    assessment_id: int,
    answer_data: AssessmentAnswerSubmit,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Submit a student's answer to an assessment and automatically grade it. Requires authentication."""
    # Get assessment
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )

    # Users can only submit their own assessments
    if assessment.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to submit this assessment"
        )

    # Check if already submitted
    if assessment.submitted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment has already been submitted"
        )

    # Update assessment with answer
    assessment.student_answer = answer_data.student_answer
    assessment.submitted_at = datetime.now(timezone.utc)

    # Commit the submission first
    db.commit()
    db.refresh(assessment)

    # Automatically grade the assessment using LLM
    try:
        grading_service = get_grading_service(db)
        competency_service = get_competency_service(db)
        score, feedback = grading_service.grade_assessment(assessment, competency_service=competency_service)

        # Update assessment with grading results
        assessment.score = score
        assessment.feedback = feedback
        assessment.graded_at = datetime.now(timezone.utc)
        assessment.graded_by = GradingSource.AUTO

        db.commit()
        db.refresh(assessment)

        safe_assessment_id = _sanitize_log_value(str(assessment_id))
        logger.info(f"Student submitted and auto-graded assessment {safe_assessment_id} - Score: {score}/{assessment.max_score}")
    except Exception as e:
        logger.error(f"Failed to auto-grade assessment {safe_assessment_id}: {str(e)}")
        # Continue even if grading fails - assessment is submitted but not graded
        logger.info(f"Assessment {safe_assessment_id} submitted but not graded due to error")

    return AssessmentResponse.model_validate(assessment)

@app.post("/assessments/{assessment_id}/grade", response_model=AssessmentResponse)
async def grade_assessment(
    assessment_id: int,
    grade_data: AssessmentGradeRequest,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin_user)
):
    """Grade or override assessment grading (admin only). Can override auto-graded assessments."""
    # Get assessment
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )

    # Check if submitted
    if not assessment.submitted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment must be submitted before grading"
        )

    # Check if this is an override of existing grading
    is_override = assessment.graded_at is not None
    was_auto_graded = assessment.graded_by == GradingSource.AUTO

    # Update assessment with grade
    assessment.score = grade_data.score
    if grade_data.max_score:
        assessment.max_score = grade_data.max_score
    if grade_data.feedback:
        assessment.feedback = grade_data.feedback
    assessment.graded_at = datetime.now(timezone.utc)
    assessment.graded_by = GradingSource.ADMIN

    # Track override timestamp if this is overriding an auto-grade
    if is_override and was_auto_graded:
        assessment.overridden_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(assessment)

    action = "overrode auto-grade for" if is_override and was_auto_graded else "graded"
    safe_assessment_id = _sanitize_log_value(str(assessment_id))
    safe_current_admin = _sanitize_log_value(str(current_admin.id))
    safe_score = _sanitize_log_value(str(grade_data.score))
    safe_max_score = _sanitize_log_value(str(assessment.max_score))
    logger.info(f"Admin {safe_current_admin} {action} assessment {safe_assessment_id}: {safe_score}/{safe_max_score}")
    return AssessmentResponse.model_validate(assessment)

# Root endpoint
# ---- Competency Endpoints ----

@app.get("/students/{student_id}/competencies", response_model=StudentCompetenciesResponse)
async def get_student_competencies(
    student_id: int,
    topic: str | None = None,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Get competency records for a student, optionally filtered by topic."""
    if current_user.id != student_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these competencies"
        )

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter 'topic' is required"
        )

    competency_service = get_competency_service(db)
    competencies = competency_service.get_student_competencies(student_id, topic)

    safe_student_id = _sanitize_log_value(str(student_id))
    safe_topic = _sanitize_log_value(topic)
    logger.info(f"Retrieved competencies for student {safe_student_id} in topic {safe_topic}")

    return StudentCompetenciesResponse(
        student_id=student_id,
        topic=topic,
        competencies=[ConceptCompetencyResponse.model_validate(c) for c in competencies]
    )


@app.get("/students/{student_id}/mastery/{topic}", response_model=MasterySummaryResponse)
async def get_student_mastery(
    student_id: int,
    topic: str,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Get a mastery summary for a student in a specific topic."""
    if current_user.id != student_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this mastery data"
        )

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    competency_service = get_competency_service(db)
    summary = competency_service.get_mastery_summary(student_id, topic)

    safe_student_id = _sanitize_log_value(str(student_id))
    safe_topic = _sanitize_log_value(topic)
    logger.info(f"Retrieved mastery summary for student {safe_student_id} in topic {safe_topic}")

    return MasterySummaryResponse(**summary)


@app.get("/students/{student_id}/recommended-concepts/{topic}", response_model=RecommendedConceptsResponse)
async def get_recommended_concepts(
    student_id: int,
    topic: str,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Get recommended next concepts to learn for a student in a topic."""
    if current_user.id != student_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these recommendations"
        )

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    competency_service = get_competency_service(db)
    recommendations = competency_service.get_next_concepts_to_learn(student_id, topic)

    safe_student_id = _sanitize_log_value(str(student_id))
    safe_topic = _sanitize_log_value(topic)
    logger.info(f"Retrieved recommended concepts for student {safe_student_id} in topic {safe_topic}")

    return RecommendedConceptsResponse(
        student_id=student_id,
        topic=topic,
        recommendations=[RecommendedConceptResponse(**r) for r in recommendations]
    )


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
