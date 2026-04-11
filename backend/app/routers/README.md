# Routers - FastAPI Route Handlers

## Overview

The `routers/` directory contains FastAPI APIRouter instances that group related endpoints. These routers are included in the main application via `app.include_router()`.

## Contents

| File              | Description                                                    |
|-------------------|----------------------------------------------------------------|
| `admin.py`        | Admin-only endpoints for user management, settings & analytics |
| `auth.py`         | Registration, login, current user                              |
| `students.py`     | Student profile CRUD & progress                                |
| `chat.py`         | Chat with AI tutor, conversation history                       |
| `feedback.py`     | Message feedback submission                                    |
| `analytics.py`    | Activity event recording                                       |
| `assessments.py`  | Assessment generation, submission & grading                    |
| `exercises.py`    | Exercise listing & progress                                    |
| `competencies.py` | Concept mastery & recommendations                              |
| `reviews.py`      | Spaced repetition review sessions                              |
| `__init__.py`     | Package initialization                                         |

---

## Auth Router

**Prefix:** `/auth` | **Tags:** `auth`

| Method | Endpoint         | Description                    | Auth   |
|--------|------------------|--------------------------------|--------|
| POST   | `/auth/register` | Register new user              | Public |
| POST   | `/auth/login`    | Login with email/password      | Public |
| GET    | `/auth/me`       | Get current authenticated user | User   |

### Business Logic

- **Registration**: Rate limited (5/min). Users with `@usach.cl` email are auto-activated; others require admin approval. Initializes knowledge levels for all five topics as "beginner."
- **Login**: Rate limited (5/min). Updates `last_login` timestamp. Returns JWT token.
- **Me**: Returns authenticated user's profile data.

---

## Students Router

**Prefix:** `/students` | **Tags:** `students`

| Method | Endpoint                          | Description                        | Auth       |
|--------|-----------------------------------|------------------------------------|------------|
| POST   | `/students`                       | Create new student profile         | Public     |
| GET    | `/students`                       | List all students                  | Public     |
| GET    | `/students/{student_id}`          | Get student profile by ID          | Self/Admin |
| PUT    | `/students/{student_id}`          | Update student profile             | Self       |
| GET    | `/students/{student_id}/progress` | Get comprehensive progress metrics | Self/Admin |

### Business Logic

- **Create**: Checks email uniqueness. Initializes default knowledge levels if not provided.
- **Update**: Partial updates supported (name, email, knowledge_levels, preferences). Users can only update their own profile.
- **Progress**: Aggregates conversation-based metrics via `conversation_service.compute_student_progress()`.

---

## Chat Router

**Prefix:** none | **Tags:** `chat`

| Method | Endpoint                               | Description                         | Auth       |
|--------|----------------------------------------|-------------------------------------|------------|
| POST   | `/chat`                                | Send message & get AI response      | User       |
| GET    | `/conversations/{conversation_id}`     | Get full conversation with messages | Self/Admin |
| GET    | `/students/{student_id}/conversations` | List conversations for a student    | Self/Admin |

### Business Logic

- **Chat**: Rate limited (10/min). Creates or retrieves conversation based on `conversation_id`. Selects agent by topic from `AGENT_REGISTRY`. Builds student context with adaptive learning data, injects spaced repetition reviews if due. Stores both user and assistant messages.
- **Agent selection**: `operations_research`, `linear_programming`, `mathematical_modeling`, `nonlinear_programming`, `integer_programming`. Default fallback: Linear Programming Agent.

---

## Feedback Router

**Prefix:** none | **Tags:** `feedback`

| Method | Endpoint    | Description                      | Auth |
|--------|-------------|----------------------------------|------|
| POST   | `/feedback` | Create feedback for a message    | User |

### Business Logic

- Verifies a message exists before creating feedback (404 if not found).
- Accepts `message_id`, `rating`, `is_helpful`, and `comment`.
- Returns 201 on success.

---

## Analytics Router

**Prefix:** `/analytics` | **Tags:** `analytics`

| Method | Endpoint            | Description                        | Auth |
|--------|---------------------|------------------------------------|------|
| POST   | `/analytics/events` | Record batch of activity events    | User |

### Business Logic

- Accepts `ActivityEventBatchCreate` (batch of events).
- Returns count of recorded events: `{"recorded": count}`.
- Returns 201 on success.

---

## Assessments Router

**Prefix:** none | **Tags:** `assessments`

| Method | Endpoint                                  | Description                            | Auth       |
|--------|-------------------------------------------|----------------------------------------|------------|
| GET    | `/students/{student_id}/assessments`      | List assessments for a student         | Self/Admin |
| GET    | `/assessments/{assessment_id}`            | Get specific assessment by ID          | Self/Admin |
| POST   | `/assessments/generate`                   | Generate personalized assessment (LLM) | User       |
| POST   | `/assessments/generate/from-exercise`     | Generate assessment from exercise      | User       |
| POST   | `/assessments/{assessment_id}/submit`     | Submit answer & auto-grade             | User       |
| POST   | `/assessments/{assessment_id}/grade`      | Admin override grading                 | Admin      |

### Business Logic

- **List**: Filterable by `topic`, supports `skip`/`limit` pagination.
- **Generate**: Rate limited (5/min). Uses LLM to create personalized assessment. Max score: 7.0 (Chilean scale).
- **Generate from exercise**: Rate limited (5/min). Supports `practice` (use directly) and `similar` (LLM generates similar) modes. Exercise gating enforces sequential progression — 403 if prerequisite exercises not completed.
- **Submit**: Rate limited (10/min). Prevents resubmission. Auto-grades via `grading_service` with `GradingSource.AUTO`.
- **Admin grade**: Requires assessment to be submitted first. Sets `GradingSource.ADMIN` and tracks override timestamp.

---

## Exercises Router

**Prefix:** `/exercises` | **Tags:** `exercises`

| Method | Endpoint                    | Description                                   | Auth   |
|--------|-----------------------------|-----------------------------------------------|--------|
| GET    | `/exercises`                | List available exercises                      | Public |
| GET    | `/exercises/progress`       | Exercises with locked/completed status        | User   |
| GET    | `/exercises/{exercise_id}`  | Get exercise preview (statement, no solution) | Public |

### Business Logic

- **List**: Filterable by `topic`. Returns exercises from `exercise_registry`.
- **Progress**: Enriches exercises with student-specific locked/completed status via `get_exercises_with_progress()`.
- **Preview**: Returns an exercise statement only (no solution). 404 if not found.

---

## Competencies Router

**Prefix:** none | **Tags:** `competencies`

| Method | Endpoint                                                  | Description                    | Auth       |
|--------|-----------------------------------------------------------|--------------------------------|------------|
| GET    | `/students/{student_id}/competencies`                     | Get competency records         | Self/Admin |
| GET    | `/students/{student_id}/mastery/{topic}`                  | Get mastery summary for topic  | Self/Admin |
| GET    | `/students/{student_id}/recommended-concepts/{topic}`     | Get recommended next concepts  | Self/Admin |

### Business Logic

- **Competencies**: Requires `topic` query parameter (400 if missing).
- **Mastery**: Returns mastery summary for a specific topic using Bloom taxonomy concept hierarchy.
- **Recommendations**: Suggests next concepts to learn based on the current mastery state.

---

## Reviews Router

**Prefix:** none | **Tags:** `reviews`

| Method | Endpoint                                  | Description                                | Auth       |
|--------|-------------------------------------------|--------------------------------------------|------------|
| GET    | `/students/{student_id}/reviews/due`      | Get concepts due for review                | Self/Admin |
| POST   | `/students/{student_id}/reviews/start`    | Start a review session for a concept       | Self       |
| POST   | `/reviews/{review_id}/complete`           | Complete review with quality rating (0-5)  | Owner      |

### Business Logic

- **Due reviews**: Filterable by `topic`, `limit` defaults to 5. Uses SM-2 spaced repetition algorithm.
- **Start review**: Verifies competency exists (404 if not found). Returns 201 with session details.
- **Complete review**: Validates review exists and is not yet completed. Accepts `performance_quality` (0–5) and `response_time_seconds`. Returns updated mastery score, mastery level, and ease factor.

---

## Admin Router

**Prefix:** `/admin` | **Tags:** `admin`

### User Management Endpoints

| Method | Endpoint                        | Description                          | Auth  |
|--------|---------------------------------|--------------------------------------|-------|
| GET    | `/admin/users`                  | List all users with progress metrics | Admin |
| GET    | `/admin/users/{user_id}`        | Get detailed user information        | Admin |
| PUT    | `/admin/users/{user_id}/status` | Activate or deactivate user account  | Admin |
| PUT    | `/admin/users/{user_id}/role`   | Change user role (user/admin)        | Admin |

### System Endpoints

| Method | Endpoint             | Description                     | Auth  |
|--------|----------------------|---------------------------------|-------|
| GET    | `/admin/settings`    | Get system settings (read-only) | Admin |
| GET    | `/admin/stats`       | Get system-wide statistics      | Admin |

### Analytics Endpoints

All analytics endpoints accept a `days` query parameter (default: `30`) to control the date range.

| Method | Endpoint                       | Description                              | Auth  |
|--------|--------------------------------|------------------------------------------|-------|
| GET    | `/admin/analytics/summary`     | Combined analytics summary (all metrics) | Admin |
| GET    | `/admin/analytics/dau`         | Daily active users over time             | Admin |
| GET    | `/admin/analytics/sessions`    | Average session duration by day          | Admin |
| GET    | `/admin/analytics/peak-hours`  | Peak usage hours                         | Admin |
| GET    | `/admin/analytics/pages`       | Page popularity metrics                  | Admin |
| GET    | `/admin/analytics/topics`      | Topic popularity metrics                 | Admin |
| GET    | `/admin/analytics/engagement`  | User engagement metrics                  | Admin |

### Response Examples

#### GET /admin/users

```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2026-01-01T00:00:00Z",
    "last_login": "2026-01-05T10:30:00Z",
    "total_conversations": 15,
    "total_assessments": 5,
    "average_score": 85.5
  }
]
```

#### GET /admin/settings

```json
{
  "llm_provider": "gemini",
  "llm_model": "gemini-1.5-flash",
  "temperature": 0.4,
  "max_tokens": 2000,
  "version": "1.0.0",
  "debug": false,
  "session_timeout_minutes": 60
}
```

#### GET /admin/stats

```json
{
  "total_users": 100,
  "active_users": 85,
  "total_conversations": 1500,
  "total_assessments": 450,
  "average_assessment_score": 78.3
}
```

#### GET /admin/analytics/summary?days=30

Returns a combined `AnalyticsSummaryResponse` with all analytics in one call:

```json
{
  "dau": { ... },
  "session_duration": { ... },
  "peak_usage": { ... },
  "page_popularity": { ... },
  "topic_popularity": { ... },
  "engagement": { ... }
}
```

Each subfield matches the response of its individual endpoint (`/analytics/dau`, `/analytics/sessions`, etc.).

### Admin Business Logic

- **List users**: Returns all users with computed progress metrics (conversation count, assessment stats). Supports `skip` and `limit` pagination parameters.
- **User status**: Admins cannot deactivate their own account (self-protection).
- **Role change**: Admins cannot change their own role (prevents lockout). Only `"user"` and `"admin"` roles are valid.
- **Statistics**: Computed in real-time from the database (total/active user counts, conversation/assessment totals, average scores).
- **Analytics**: Computed in real-time via `AnalyticsService`. All endpoints accept a `days` parameter (default: `30`).

---

## Security

All endpoints (except public ones) require:
1. Valid JWT token
2. Appropriate user role

**Auth levels:**
- **Public**: No authentication required
- **User**: Valid JWT token via `Depends(get_current_user)`
- **Self/Admin**: Authenticated user can only access their own data; admins can access any
- **Admin**: User role = `admin` via `Depends(get_current_admin_user)`

Admin actions are logged with sanitized values (log injection prevention via `_sanitize_log_value()`).

## Usage

### Including the Router

In `main.py`:

```python
from .routers import admin

app.include_router(admin.router)
```

### Creating a New Router

1. Create a new file in `routers/`:

```python
# routers/reports.py
from fastapi import APIRouter, Depends
from ..auth import get_current_admin_user

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/weekly")
async def weekly_report(
    current_admin = Depends(get_current_admin_user)
):
    return {"report": "weekly data"}
```

2. Include in `main.py`:

```python
from .routers import admin, reports

app.include_router(admin.router)
app.include_router(reports.router)
```

## Changelog

- **v1.0.0** (2026-01-05): Initial documentation
- **v1.1.0** (2026-02-03): Added some tools, exercise features, basic user restrictiveness to `@usach` domain
- **v1.1.1** (2026-02-07): New exercises were added.
- **v1.2.1** (2026-02-13): New functionality for locked and unlocked exercises.
- **v1.3.1** (2026-02-16): Added concept-level mastery tracking — when assessments are graded.
- **v1.3.2** (2026-02-17): Added and fixed logout functionality.
- **v1.3.3** (2026-02-17): Fixed assessment behavior.
- **v1.4.3** (2026-02-18): Record student's activity.
- **v1.5.3** (2026-02-19): Spaced Repetition System.
- **v1.5.4** (2026-02-25): Fixed some bugs.
- **v1.6.4** (2026-02-27): Added testing implementation.
- **v1.6.5** (2026-04-03): Security, routing and main.py improvements.
- **v1.6.6** (2026-04-06): Coverage tests.
- **v1.6.7** (2026-04-11): Code review and exercises.