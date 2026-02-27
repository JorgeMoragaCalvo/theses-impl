# Tests

Test suite for the AI Tutoring System backend.

## Structure

- **`unit/`** — Fast, isolated unit tests that mock all external dependencies.
- **`integration/`** — Integration tests that exercise API endpoints through the FastAPI `TestClient`.
- **`conftest.py`** — Shared fixtures: in-memory SQLite database, mocked LLM service, test client, pre-created users, and auth headers.

Runs `python -m pytest tests/ -v --tb=short` from the backend/ directory