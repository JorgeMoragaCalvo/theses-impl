import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import ReviewSession, Student, StudentCompetency, get_db
from ..enums import UserRole
from ..models import (
    CompleteReviewRequest,
    CompleteReviewResponse,
    DueReviewResponse,
    DueReviewsResponse,
    StartReviewRequest,
    StartReviewResponse,
)
from ..rate_limit import limiter
from ..services.spaced_repetition_service import get_spaced_repetition_service
from ..utils import sanitize_log_value

logger = logging.getLogger(__name__)

router = APIRouter(tags=["reviews"])


@router.get("/students/{student_id}/reviews/due", response_model=DueReviewsResponse)
async def get_due_reviews(
    student_id: int,
    topic: str | None = None,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):
    """Get concepts due for spaced-repetition review."""
    if current_user.id != student_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these reviews",
        )

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    srs = get_spaced_repetition_service(db)
    due = srs.get_due_reviews(student_id, topic=topic, limit=limit)

    safe_sid = sanitize_log_value(student_id)
    logger.info(f"Retrieved {len(due)} due reviews for student {safe_sid}")

    return DueReviewsResponse(
        student_id=student_id,
        topic=topic,
        due_reviews=[DueReviewResponse.model_validate(c) for c in due],
    )


@router.post("/students/{student_id}/reviews/start", response_model=StartReviewResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def start_review(
    request: Request,
    student_id: int,
    review_request: StartReviewRequest,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):
    """Start a review session for a specific concept."""
    if current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to start reviews for this student",
        )

    # Verify the competency exists
    competency = db.query(StudentCompetency).filter(
        StudentCompetency.student_id == student_id,
        StudentCompetency.concept_id == review_request.concept_id,
    ).first()

    if not competency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No competency record found for concept '{review_request.concept_id}'",
        )

    srs = get_spaced_repetition_service(db)
    session = srs.create_review_session(student_id, review_request.concept_id)

    return StartReviewResponse(
        review_session_id=session.id,
        concept_id=session.concept_id,
        concept_name=competency.concept_name,
        scheduled_at=session.scheduled_at,
    )


@router.post("/reviews/{review_id}/complete", response_model=CompleteReviewResponse)
async def complete_review(
    review_id: int,
    request: CompleteReviewRequest,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):
    """Complete a review session with a performance quality rating (0-5)."""
    review = db.query(ReviewSession).filter(ReviewSession.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review session not found",
        )

    if review.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to complete this review session",
        )

    if review.completed_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review session already completed",
        )

    srs = get_spaced_repetition_service(db)
    try:
        completed = srs.complete_review(
            review_session_id=review_id,
            performance_quality=request.performance_quality,
            response_time_seconds=request.response_time_seconds,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Re-read competency for the response
    competency = db.query(StudentCompetency).filter(
        StudentCompetency.student_id == review.student_id,
        StudentCompetency.concept_id == review.concept_id,
    ).first()

    return CompleteReviewResponse(
        review_session_id=completed.id,
        concept_id=completed.concept_id,
        performance_quality=completed.performance_quality,
        next_review_scheduled=completed.next_review_scheduled,
        updated_mastery_score=round(competency.mastery_score, 3),
        updated_mastery_level=competency.mastery_level.value,
        updated_ease_factor=round(competency.decay_factor, 3),
    )
