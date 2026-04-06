import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import Student, get_db
from ..enums import UserRole
from ..models import (
    ConceptCompetencyResponse,
    MasterySummaryResponse,
    RecommendedConceptResponse,
    RecommendedConceptsResponse,
    StudentCompetenciesResponse,
)
from ..services.competency_service import get_competency_service
from ..utils import sanitize_log_value

logger = logging.getLogger(__name__)

router = APIRouter(tags=["competencies"])


@router.get(
    "/students/{student_id}/competencies", response_model=StudentCompetenciesResponse
)
async def get_student_competencies(
    student_id: int,
    topic: str | None = None,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):
    """Get competency records for a student, optionally filtered by topic."""
    if current_user.id != student_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these competencies",
        )

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter 'topic' is required",
        )

    competency_service = get_competency_service(db)
    competencies = competency_service.get_student_competencies(student_id, topic)

    safe_student_id = sanitize_log_value(student_id)
    safe_topic = sanitize_log_value(topic)
    logger.info(
        f"Retrieved competencies for student {safe_student_id} in topic {safe_topic}"
    )

    return StudentCompetenciesResponse(
        student_id=student_id,
        topic=topic,
        competencies=[
            ConceptCompetencyResponse.model_validate(c) for c in competencies
        ],
    )


@router.get(
    "/students/{student_id}/mastery/{topic}", response_model=MasterySummaryResponse
)
async def get_student_mastery(
    student_id: int,
    topic: str,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):
    """Get a mastery summary for a student in a specific topic."""
    if current_user.id != student_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this mastery data",
        )

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )

    competency_service = get_competency_service(db)
    summary = competency_service.get_mastery_summary(student_id, topic)

    safe_student_id = sanitize_log_value(student_id)
    safe_topic = sanitize_log_value(topic)
    logger.info(
        f"Retrieved mastery summary for student {safe_student_id} in topic {safe_topic}"
    )

    return MasterySummaryResponse(**summary)


@router.get(
    "/students/{student_id}/recommended-concepts/{topic}",
    response_model=RecommendedConceptsResponse,
)
async def get_recommended_concepts(
    student_id: int,
    topic: str,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):
    """Get recommended next concepts to learn for a student in a topic."""
    if current_user.id != student_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these recommendations",
        )

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )

    competency_service = get_competency_service(db)
    recommendations = competency_service.get_next_concepts_to_learn(student_id, topic)

    safe_student_id = sanitize_log_value(student_id)
    safe_topic = sanitize_log_value(topic)
    logger.info(
        f"Retrieved recommended concepts for student {safe_student_id} in topic {safe_topic}"
    )

    return RecommendedConceptsResponse(
        student_id=student_id,
        topic=topic,
        recommendations=[RecommendedConceptResponse(**r) for r in recommendations],
    )
