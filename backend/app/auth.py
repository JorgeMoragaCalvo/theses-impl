# UPDATED: 2025-11-11 23:00 - Added byte truncation for bcrypt 72-byte limit
import logging
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db, Student, UserRole

"""
Authentication and authorization utilities.
Handles password hashing, JWT token creation/validation, and user authentication.
"""

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer security scheme
security = HTTPBearer()

# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7  # Token valid for 7 days for session persistence


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Truncates the plain password to 72 bytes to match the behavior
    of get_password_hash() for consistency. Note: This is 72 BYTES,
    not characters (important for UTF-8 multibyte characters).

    Args:
        plain_password: The plain text password
        hashed_password: The hashed password to compare against

    Returns:
        True if the password matches, False otherwise
    """
    # DEBUG: Log password lengths
    print("[DEBUG] verify_password called - UPDATED CODE 2025-11-11 23:00")
    print(f"[DEBUG] Original password length: {len(plain_password)} chars, {len(plain_password.encode())} bytes")

    # Truncate to 72 BYTES (not characters) to match hashing behavior
    password_bytes = plain_password.encode()[:72]
    plain_password_truncated = password_bytes.decode(errors='ignore')

    print(f"[DEBUG] Truncated password length: {len(plain_password_truncated)} chars, {len(plain_password_truncated.encode())} bytes")

    return pwd_context.verify(plain_password_truncated, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Bcrypt has a 72-byte limit, so we truncate the password to 72 bytes
    (not 72 characters, which may differ for UTF-8 multibyte characters).

    Args:
        password: The plain text password to hash

    Returns:
        The hashed password
    """
    # DEBUG: Log password lengths
    print("[DEBUG] get_password_hash called - UPDATED CODE 2025-11-11 23:00")
    print(f"[DEBUG] Original password length: {len(password)} chars, {len(password.encode())} bytes")

    # Truncate to 72 BYTES (not characters) to comply with bcrypt's limit
    password_bytes = password.encode()[:72]
    password_truncated = password_bytes.decode(errors='ignore')

    print(f"[DEBUG] Truncated password length: {len(password_truncated)} chars, {len(password_truncated.encode())} bytes")

    return pwd_context.hash(password_truncated)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary containing the data to encode in the token
        expires_delta: Optional timedelta for token expiration

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)

    logger.debug(f"Created JWT token for user_id: {data.get('sub')}, expires: {expire}")

    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Args:
        token: The JWT token to decode

    Returns:
        Dictionary containing the decoded token data

    Raises:
        HTTPException: If the token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        logger.debug(f"Successfully decoded JWT token for user_id: {payload.get('sub')}")
        return payload
    except JWTError as e:
        # Log the specific JWT error for debugging
        logger.error(f"JWT validation failed: {type(e).__name__}: {str(e)}")
        logger.error(f"Token (first 20 chars): {token[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def authenticate_user(db: Session, email: str, password: str) -> Student | None:
    """
    Authenticate a user by email and password.

    Args:
        db: Database session
        email: User's email
        password: Plain text password

    Returns:
        Student object if the authentication is successful, None otherwise
    """
    student = db.query(Student).filter(Student.email == email).first()
    if not student:
        return None
    if not verify_password(password, str(student.password_hash)):
        return None
    if not student.is_active:
        return None
    return student


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Student:
    """
    Dependency to get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token from request
        db: Database session

    Returns:
        Current authenticated Student object

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id: int = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    student = db.query(Student).filter(Student.id == user_id).first()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not student.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return student


async def get_current_active_user(
    current_user: Student = Depends(get_current_user)
) -> Student:
    """
    Dependency to get the current active user.

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        Current active Student object

    Raises:
        HTTPException: If the user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: Student = Depends(get_current_user)
) -> Student:
    """
    Dependency to get the current admin user (role-based authorization).

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        Current admin Student object

    Raises:
        HTTPException: If the user is not an admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin role required."
        )
    return current_user
