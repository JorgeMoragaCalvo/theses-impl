"""
Shared test fixtures for the AI Tutoring System test suite.

Provides:
- SQLite in-memory database engine and sessions
- Mocked LLM service
- FastAPI TestClient with dependency overrides
- Pre-created test users (student + admin) with JWT auth headers
- Singleton reset between tests
- Test environment variables
"""
import os

# ---------------------------------------------------------------------------
# 1. Environment variables — MUST be set before any app imports so that
#    Settings() (which runs at import-time) picks them up.
# ---------------------------------------------------------------------------
os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests-only")
os.environ.setdefault("GOOGLE_API_KEY", "fake-key-for-tests")
os.environ.setdefault("LLM_PROVIDER", "gemini")

# Patch create_engine BEFORE app.database is imported so the module-level
# engine creation doesn't fail with PostgreSQL-only kwargs on SQLite.
from unittest.mock import MagicMock, patch  # noqa: E402

import sqlalchemy  # noqa: E402

_original_create_engine = sqlalchemy.create_engine

def _patched_create_engine(url, **kwargs):
    """Strip PostgreSQL-specific kwargs when using SQLite."""
    if str(url).startswith("sqlite"):
        kwargs.pop("pool_size", None)
        kwargs.pop("max_overflow", None)
        kwargs.pop("pool_pre_ping", None)
        kwargs.setdefault("connect_args", {"check_same_thread": False})
    return _original_create_engine(url, **kwargs)

patch("sqlalchemy.create_engine", _patched_create_engine).start()
# Also patch the reference in sqlalchemy.engine.create
import sqlalchemy.engine.create  # noqa: E402

sqlalchemy.engine.create.create_engine = _patched_create_engine

import pytest  # noqa: E402
from app.auth import create_access_token, get_password_hash  # noqa: E402
from app.database import Base, Student, UserRole, get_db  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

# ---------------------------------------------------------------------------
# 2. SQLite in-memory engine & session
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def test_engine():
    """Create an SQLite in-memory engine shared across all tests in the session."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def test_db(test_engine):
    """
    Function-scoped SQLAlchemy session.

    Each test gets a fresh transaction rolled back at the end so
    tests don't interfere with each other.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    TestSession = sessionmaker(bind=connection)
    session = TestSession()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# 3. Mocked LLM service
# ---------------------------------------------------------------------------

@pytest.fixture()
def fake_llm_service():
    """Return a MagicMock standing in for LLMService."""
    mock = MagicMock()
    mock.generate_response.return_value = '{"score": 5.0, "feedback": "Good job."}'
    mock.a_generate_response.return_value = '{"score": 5.0, "feedback": "Good job."}'
    mock.generate_response_with_tools.return_value = "Tool response"
    mock.a_generate_response_with_tools.return_value = "Tool response"
    mock.get_provider_info.return_value = {"provider": "mock", "model": "mock-model"}
    return mock


# ---------------------------------------------------------------------------
# 4. FastAPI TestClient
# ---------------------------------------------------------------------------

@pytest.fixture()
def client(test_db, fake_llm_service):
    """
    FastAPI TestClient with overridden dependencies:
    - get_db → test_db
    - init_db patched out (lifespan tries to connect to production DB)
    - SessionLocal patched to use the test engine
    - LLMService singleton replaced with mock
    - Taxonomy registry returns empty data
    """
    fake_registry = MagicMock()
    fake_registry.get_concepts_for_topic.return_value = []
    fake_registry.get_concept.return_value = None
    fake_registry.concept_exists.return_value = False
    fake_registry.get_all_concept_ids.return_value = []

    with (
        patch("app.database.init_db"),
        patch("app.database.SessionLocal", return_value=test_db),
        patch("app.services.llm_service.get_llm_service", return_value=fake_llm_service),
        patch("app.services.llm_service._llm_service", fake_llm_service),
        patch("app.services.competency_service.get_taxonomy_registry", return_value=fake_registry),
        patch("app.services.competency_service._taxonomy_registry", fake_registry),
        patch("app.main.init_db"),
        patch("app.main.SessionLocal", return_value=test_db),
        patch("app.main.get_competency_service"),
    ):
        from app.main import app

        def _override_get_db():
            yield test_db

        app.dependency_overrides[get_db] = _override_get_db

        with TestClient(app, raise_server_exceptions=False) as tc:
            yield tc

        app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 5. Pre-created users
# ---------------------------------------------------------------------------

@pytest.fixture()
def test_user(test_db):
    """Create and return a regular active student."""
    user = Student(
        name="Test Student",
        email="student@usach.cl",
        password_hash=get_password_hash("testpassword123"),
        role=UserRole.USER,
        is_active=True,
        knowledge_levels={
            "operations_research": "beginner",
            "mathematical_modeling": "beginner",
            "linear_programming": "beginner",
            "integer_programming": "beginner",
            "nonlinear_programming": "beginner",
        },
        preferences={},
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture()
def test_admin(test_db):
    """Create and return an admin user."""
    admin = Student(
        name="Admin User",
        email="admin@usach.cl",
        password_hash=get_password_hash("adminpassword123"),
        role=UserRole.ADMIN,
        is_active=True,
        knowledge_levels={
            "operations_research": "advanced",
            "mathematical_modeling": "advanced",
            "linear_programming": "advanced",
            "integer_programming": "advanced",
            "nonlinear_programming": "advanced",
        },
        preferences={},
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin


# ---------------------------------------------------------------------------
# 6. Auth headers
# ---------------------------------------------------------------------------

@pytest.fixture()
def auth_headers(test_user):
    """JWT Bearer headers for the regular test user."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin_auth_headers(test_admin):
    """JWT Bearer headers for the admin user."""
    token = create_access_token(data={"sub": str(test_admin.id)})
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# 7. Reset singletons between tests
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset cached singletons so each test starts fresh."""
    import app.services.competency_service as comp_mod
    import app.services.llm_service as llm_mod

    old_llm = llm_mod._llm_service
    old_tax = comp_mod._taxonomy_registry

    yield

    llm_mod._llm_service = old_llm
    comp_mod._taxonomy_registry = old_tax
