import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..auth import get_current_admin_user, get_current_user
from ..database import Assessment, Conversation, Student, get_db
from ..enums import GradingSource, UserRole
from ..models import (
    AssessmentAnswerSubmit,
    AssessmentGenerate,
    AssessmentGradeRequest,
    AssessmentResponse,
    ExerciseAssessmentGenerate,
)
from ..rate_limit import limiter
from ..services.assessment_service import get_assessment_service
from ..services.competency_service import get_competency_service
from ..services.exercise_assessment_service import (
    get_exercise_assessment_service,
    get_exercise_registry,
)
from ..services.exercise_progress_service import (
    compute_max_unlocked_rank,
    get_completed_exercise_ids,
)
from ..services.grading_service import get_grading_service
from ..utils import sanitize_log_value

logger = logging.getLogger(__name__)

router = APIRouter(tags=["assessments"])


@router.get("/students/{student_id}/assessments", response_model=list[AssessmentResponse])
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


@router.get("/assessments/{assessment_id}", response_model=AssessmentResponse)
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


@router.post("/assessments/generate", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def generate_assessment(
    request: Request,
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


@router.post("/assessments/generate/from-exercise", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def generate_assessment_from_exercise(
    request: Request,
    exercise_data: ExerciseAssessmentGenerate,
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
    topic = registry.get_topic_for_exercise(exercise_data.exercise_id)

    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise '{exercise_data.exercise_id}' not found"
        )

    # Gating: check if the exercise is locked for this student
    exercises = registry.list_exercises_by_topic(topic)
    target_exercise = next((ex for ex in exercises if ex["id"] == exercise_data.exercise_id), None)
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
            exercise_id=exercise_data.exercise_id,
            mode=exercise_data.mode
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
    safe_exercise_id = sanitize_log_value(exercise_data.exercise_id)
    safe_mode = sanitize_log_value(exercise_data.mode)

    logger.info(
        f"Generated exercise assessment {new_assessment.id} for student {student_id} "
        f"(exercise: {safe_exercise_id}, mode: {safe_mode})"
    )
    return AssessmentResponse.model_validate(new_assessment)


@router.post("/assessments/{assessment_id}/submit", response_model=AssessmentResponse)
@limiter.limit("10/minute")
async def submit_assessment_answer(
    request: Request,
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

    safe_assessment_id = sanitize_log_value(assessment_id)

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

        logger.info(f"Student submitted and auto-graded assessment {safe_assessment_id} - Score: {score}/{assessment.max_score}")
    except Exception as e:
        logger.error(f"Failed to auto-grade assessment {safe_assessment_id}: {str(e)}")
        # Continue even if grading fails - assessment is submitted but not graded
        logger.info(f"Assessment {safe_assessment_id} submitted but not graded due to error")

    return AssessmentResponse.model_validate(assessment)


@router.post("/assessments/{assessment_id}/grade", response_model=AssessmentResponse)
@limiter.limit("5/minute")
async def grade_assessment(
    request: Request,
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
    safe_assessment_id = sanitize_log_value(assessment_id)
    safe_current_admin = sanitize_log_value(current_admin.id)
    safe_score = sanitize_log_value(grade_data.score)
    safe_max_score = sanitize_log_value(assessment.max_score)
    logger.info(f"Admin {safe_current_admin} {action} assessment {safe_assessment_id}: {safe_score}/{safe_max_score}")
    return AssessmentResponse.model_validate(assessment)
