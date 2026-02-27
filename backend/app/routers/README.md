# Routers - FastAPI Route Handlers

## Overview

The `routers/` directory contains FastAPI APIRouter instances that group related endpoints. These routers are included in the main application via `app.include_router()`.

## Contents

| File          | Description                                                    |
|---------------|----------------------------------------------------------------|
| `admin.py`    | Admin-only endpoints for user management, settings & analytics |
| `__init__.py` | Package initialization                                         |

## Admin Router

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

## Business Logic

### User Management

- **List users**: Returns all users with computed progress metrics (conversation count, assessment stats). Supports `skip` and `limit` pagination parameters.
- **User status**: Admins cannot deactivate their own account (self-protection)
- **Role change**: Admins cannot change their own role (prevents lockout). Only `"user"` and `"admin"` roles are valid.

### Statistics

System stats are computed in real-time from the database:
- Total and active user counts
- Conversation and assessment totals
- Average assessment scores (excluding ungraded)

### Analytics

Analytics data is computed in real-time via `AnalyticsService`:
- **DAU** – Daily active user counts over time
- **Session duration** – Average session length per day
- **Peak hours** – Most active hours of the day
- **Page popularity** – Most visited pages
- **Topic popularity** – Most studied topics
- **Engagement** - User engagement metrics
- **Summary** – All of the above in a single response

All analytics endpoints accept a `days` parameter (default: `30`) to control the lookback window.

### Security

All admin endpoints require:
1. Valid JWT token
2. User role = `admin`

Enforced via `Depends(get_current_admin_user)` dependency.

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