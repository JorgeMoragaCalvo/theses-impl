# Integration Tests

End-to-end tests that exercise API endpoints through the FastAPI `TestClient` with an in-memory SQLite database. External services (LLM, taxonomy registry) are mocked, but the full request/response cycle — routing, dependency injection, database queries, and response serialization — is tested.

## Endpoints covered

- **Admin** (`test_admin_endpoints.py`, `test_admin_extended.py`) — admin-only management endpoints.
- **Analytics** (`test_analytics_endpoints.py`) — activity event ingestion and dashboard metrics.
- **Assessment** (`test_assessment_endpoints.py`, `test_assessment_extended.py`) — assessment creation, submission, and grading.
- **Auth** (`test_auth_endpoints.py`) — registration, login, and token handling.
- **Chat** (`test_chat_endpoint.py`) — conversational tutoring endpoint.
- **Competency** (`test_competency_endpoints.py`) — concept-mastery endpoints.
- **Exercise** (`test_exercise_endpoints.py`) — pre-built exercise endpoints.
- **Feedback** (`test_feedback_endpoints.py`) — message-feedback endpoints.
- **Review** (`test_review_endpoints.py`) — spaced-repetition review endpoints.
- **Student** (`test_student_endpoints.py`) — student profile endpoints.
