from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import Student, get_db
from ..enums import Topic
from ..services.exercise_assessment_service import (
    get_exercise_assessment_service,
    get_exercise_registry,
)
from ..services.exercise_progress_service import get_exercises_with_progress

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("")
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


@router.get("/progress")
async def list_exercises_with_progress(
    topic: Topic | None = None,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):
    """List exercises enriched with locked/completed status for the current student."""
    return get_exercises_with_progress(db, current_user.id, topic)


@router.get("/{exercise_id}")
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
