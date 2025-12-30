import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any

from ..auth import get_current_admin_user
from ..config import settings
from ..database import get_db, Student, Conversation, Assessment, UserRole
from ..models import StudentResponse

"""
Admin-only endpoints for user and system management.
All endpoints require admin role.
"""

logger = logging.getLogger(__name__)

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

    logger.info(f"Admin {current_admin.id} viewed user {user_id} details")
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
    logger.info(f"Admin {current_admin.id} {action} user {user_id}")

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
            detail=f"Invalid role. Must be 'user' or 'admin'"
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

    logger.info(f"Admin {current_admin.id} changed user {user_id} role to {role}")

    return {
        "message": f"User role updated successfully",
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
        Student.is_active == True
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
