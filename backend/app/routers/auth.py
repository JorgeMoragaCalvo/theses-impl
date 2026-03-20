import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
)
from ..database import Student, get_db
from ..enums import UserRole
from ..models import (
    RegistrationPendingResponse,
    StudentLogin,
    StudentRegister,
    StudentResponse,
    TokenResponse,
)
from ..rate_limit import limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# Allowed email domain for automatic activation
ALLOWED_EMAIL_DOMAIN = "usach.cl"


@router.post("/register", response_model=TokenResponse | RegistrationPendingResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(request: Request, user_data: StudentRegister, db: Session = Depends(get_db)):
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

    logger.info("New user registered: %d (active: %s)", new_student.id, is_allowed_domain)

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


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, credentials: StudentLogin, db: Session = Depends(get_db)):
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

    logger.info("User logged in: %d", student.id)

    return TokenResponse(
        access_token=access_token,
        user=StudentResponse.model_validate(student)
    )


@router.get("/me", response_model=StudentResponse)
async def get_me(current_user: Student = Depends(get_current_user)):
    """Get current authenticated user information."""
    return StudentResponse.model_validate(current_user)
