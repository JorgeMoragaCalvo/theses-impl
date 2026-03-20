import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_admin_user, get_current_user
from ..database import Student, get_db
from ..enums import UserRole
from ..models import (
    ProgressResponse,
    StudentCreate,
    StudentResponse,
    StudentUpdate,
)
from ..services.conversation_service import get_conversation_service
from ..utils import sanitize_log_value

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/students", tags=["students"])


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin_user),
):
    """Create a new student profile. Admin only."""
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

    logger.info("Created new student: %d", new_student.id)
    return new_student


@router.get("/{student_id}", response_model=StudentResponse)
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


@router.put("/{student_id}", response_model=StudentResponse)
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

    safe_student_id = sanitize_log_value(student_id)
    logger.info(f"Updated student: {safe_student_id}")
    return student


@router.get("", response_model=list[StudentResponse])
async def list_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(get_current_admin_user),
):
    """List all students. Admin only."""
    limit = min(limit, 100)
    students = db.query(Student).offset(skip).limit(limit).all()
    return students


@router.get("/{student_id}/progress", response_model=ProgressResponse)
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

    safe_student_id = sanitize_log_value(student_id)
    logger.info(f"Retrieved progress for student {safe_student_id}")
    return progress
