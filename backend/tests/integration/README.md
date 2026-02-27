# Integration Tests

End-to-end tests that exercise API endpoints through the FastAPI `TestClient` with an in-memory SQLite database. External services (LLM, taxonomy registry) are mocked, but the full request/response cycle — routing, dependency injection, database queries, and response serialization — is tested.

## Endpoints covered

- **Admin** — Admin-only management endpoints.
- **Assessment** — Assessment creation and submission.
- **Auth** — Registration, login, and token refresh.
- **Chat** — Conversational tutoring endpoint.
