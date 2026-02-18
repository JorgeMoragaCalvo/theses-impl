import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..auth import get_current_admin_user
from ..config import settings
from ..database import Assessment, Conversation, Student, UserRole, get_db
from ..models import AnalyticsSummaryResponse, StudentResponse
from ..services.analytics_service import get_analytics_service

"""
Admin-only endpoints for user and system management.
All endpoints require admin role.
"""

logger = logging.getLogger(__name__)


def _sanitize_log_value(value: Any) -> str:
    return str(value).replace("\r", "").replace("\n", "")


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[dict[str, Any]])
async def list_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin_user)
):
    """
    List all users with their progress metrics.
    Admin only.
    """
    # Get all students
    students = db.query(Student).offset(skip).limit(limit).all()

    # Compute progress for each student
    users_with_progress = []
    for student in students:
        # Get conversation count
        conversation_count = db.query(func.count(Conversation.id)).filter(
            Conversation.student_id == student.id
        ).scalar()

        # Get assessment stats
        assessment_count = db.query(func.count(Assessment.id)).filter(
            Assessment.student_id == student.id
        ).scalar()

        # Get average assessment score
        avg_score = db.query(func.avg(Assessment.score)).filter(
            Assessment.student_id == student.id,
            Assessment.score.isnot(None)
        ).scalar()

        users_with_progress.append({
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "role": student.role.value,
            "is_active": student.is_active,
            "created_at": student.created_at,
            "last_login": student.last_login,
            "total_conversations": conversation_count or 0,
            "total_assessments": assessment_count or 0,
            "average_score": float(avg_score) if avg_score else None
        })

    logger.info(f"Admin {current_admin.id} listed {len(users_with_progress)} users")
    return users_with_progress


@router.get("/users/{user_id}", response_model=StudentResponse)
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin_user)
):
    """
    Get detailed information about a specific user.
    Admin only.
    """
    student = db.query(Student).filter(Student.id == user_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    safe_user_id_for_log = _sanitize_log_value(user_id)
    logger.info(f"Admin {current_admin.id} viewed user {safe_user_id_for_log} details")
    return StudentResponse.model_validate(student)


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin_user)
):
    """
    Activate or deactivate a user account.
    Admin only.
    """
    student = db.query(Student).filter(Student.id == user_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent admin from deactivating themselves
    if student.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )

    student.is_active = is_active
    db.commit()
    db.refresh(student)

    action = "activated" if is_active else "deactivated"
    safe_user_id_for_log = _sanitize_log_value(user_id)
    safe_action_for_log = _sanitize_log_value(action)
    logger.info(f"Admin {current_admin.id} {safe_action_for_log} user {safe_user_id_for_log}")

    return {
        "message": f"User {action} successfully",
        "user_id": user_id,
        "is_active": is_active
    }


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin_user)
):
    """
    Update a user's role (user or admin).
    Admin only.
    """
    student = db.query(Student).filter(Student.id == user_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Validate role
    if role not in [UserRole.USER.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'user' or 'admin'"
        )

    # Prevent admin from changing their own role
    if student.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )

    # Update role
    student.role = UserRole(role)
    db.commit()
    db.refresh(student)

    safe_user_id_for_log = _sanitize_log_value(user_id)  # Ensure user_id is string for logging
    safe_role_for_log = _sanitize_log_value(role) # Sanitize role for logging
    logger.info(f"Admin {current_admin.id} changed user {safe_user_id_for_log} role to {safe_role_for_log}")

    return {
        "message": "User role updated successfully",
        "user_id": user_id,
        "role": role
    }


@router.get("/settings")
async def get_system_settings(
    current_admin: Student = Depends(get_current_admin_user)
):
    """
    Get system settings (read-only for now).
    Admin only.
    """
    logger.info(f"Admin {current_admin.id} viewed system settings")

    return {
        "llm_provider": settings.llm_provider,
        "llm_model": settings.current_model,
        "temperature": settings.temperature,
        "max_tokens": settings.max_tokens,
        "version": settings.version,
        "debug": settings.debug,
        "session_timeout_minutes": settings.session_timeout_minutes
    }


@router.get("/stats")
async def get_system_stats(
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin_user)
):
    """
    Get system-wide statistics.
    Admin only.
    """
    # Count total users
    total_users = db.query(func.count(Student.id)).scalar()

    # Count active users
    active_users = db.query(func.count(Student.id)).filter(
        Student.is_active #Student.is_active == True
    ).scalar()

    # Count total conversations
    total_conversations = db.query(func.count(Conversation.id)).scalar()

    # Count total assessments
    total_assessments = db.query(func.count(Assessment.id)).scalar()

    # Get average assessment score
    avg_assessment_score = db.query(func.avg(Assessment.score)).filter(
        Assessment.score.isnot(None)
    ).scalar()

    logger.info(f"Admin {current_admin.id} viewed system stats")

    return {
        "total_users": total_users or 0,
        "active_users": active_users or 0,
        "total_conversations": total_conversations or 0,
        "total_assessments": total_assessments or 0,
        "average_assessment_score": float(avg_assessment_score) if avg_assessment_score else None
    }


# Analytics endpoints
@router.get("/analytics/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    days: int = 30,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin_user)
):
    """Get a comprehensive analytics summary. Admin only."""
    service = get_analytics_service(db)
    logger.info(f"Admin {current_admin.id} requested analytics summary ({days} days)")
    return service.get_analytics_summary(days=days)


@router.get("/analytics/dau")
async def get_dau(
    days: int = 30,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin_user)
):
    """Daily get active users. Admin only."""
    from datetime import date, timedelta
    service = get_analytics_service(db)
    end = date.today()
    start = end - timedelta(days=days)
    return service.get_daily_active_users(start, end)


@router.get("/analytics/sessions")
async def get_session_durations(
    days: int = 30,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin_user)
):
    """Get average session duration by day. Admin only."""
    from datetime import date, timedelta
    service = get_analytics_service(db)
    end = date.today()
    start = end - timedelta(days=days)
    return service.get_avg_session_duration(start, end)


@router.get("/analytics/peak-hours")
async def get_peak_hours(
    days: int = 30,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin_user)
):
    """Get peak usage hours. Admin only."""
    from datetime import date, timedelta
    service = get_analytics_service(db)
    end = date.today()
    start = end - timedelta(days=days)
    return service.get_peak_usage_hours(start, end)


@router.get("/analytics/pages")
async def get_page_popularity(
    days: int = 30,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin_user)
):
    """Get page popularity. Admin only."""
    from datetime import date, timedelta
    service = get_analytics_service(db)
    end = date.today()
    start = end - timedelta(days=days)
    return service.get_page_popularity(start, end)


@router.get("/analytics/topics")
async def get_topic_popularity(
    days: int = 30,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin_user)
):
    """Get topic popularity. Admin only."""
    from datetime import date, timedelta
    service = get_analytics_service(db)
    end = date.today()
    start = end - timedelta(days=days)
    return service.get_topic_popularity(start, end)


@router.get("/analytics/engagement")
async def get_engagement_metrics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin_user)
):
    """Get user engagement metrics. Admin only."""
    from datetime import date, timedelta
    service = get_analytics_service(db)
    end = date.today()
    start = end - timedelta(days=days)
    return service.get_user_engagement(start, end)
