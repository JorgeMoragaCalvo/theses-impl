"""
Unit tests for app.auth — password hashing, JWT tokens, authenticate_user.
"""

import pytest
from app.auth import (
    authenticate_user,
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from fastapi import HTTPException

# ---- Password hashing ----


class TestPasswordHashing:
    def test_hash_and_verify(self):
        raw = "mysecurepassword"
        hashed = get_password_hash(raw)
        assert verify_password(raw, hashed) is True

    def test_verify_wrong_password(self):
        hashed = get_password_hash("correct")
        assert verify_password("wrong", hashed) is False

    def test_72_byte_truncation(self):
        """Passwords longer than 72 bytes are truncated consistently."""
        long_pw = "a" * 100  # 100 ASCII bytes > 72
        hashed = get_password_hash(long_pw)
        assert verify_password(long_pw, hashed) is True


# ---- JWT tokens ----


class TestJWT:
    def test_create_and_decode_token(self):
        token = create_access_token(data={"sub": "42"})
        payload = decode_access_token(token)
        assert payload["sub"] == "42"
        assert "exp" in payload

    def test_decode_expired_token(self):
        from datetime import timedelta

        token = create_access_token(
            data={"sub": "1"}, expires_delta=timedelta(seconds=-1)
        )
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        assert exc_info.value.status_code == 401

    def test_decode_invalid_token(self):
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("not.a.valid.token")
        assert exc_info.value.status_code == 401


# ---- authenticate_user ----


class TestAuthenticateUser:
    def test_success(self, test_db, test_user):
        result = authenticate_user(test_db, "student@usach.cl", "testpassword123")
        assert result is not None
        assert result.email == "student@usach.cl"

    def test_wrong_password(self, test_db, test_user):
        result = authenticate_user(test_db, "student@usach.cl", "wrongpassword")
        assert result is None

    def test_inactive_user(self, test_db):
        """Inactive user cannot authenticate even with the correct password."""
        from app.database import Student
        from app.enums import UserRole

        inactive = Student(
            name="Inactive",
            email="inactive@usach.cl",
            password_hash=get_password_hash("password123"),
            role=UserRole.USER,
            is_active=False,
        )
        test_db.add(inactive)
        test_db.commit()
        result = authenticate_user(test_db, "inactive@usach.cl", "password123")
        assert result is None
