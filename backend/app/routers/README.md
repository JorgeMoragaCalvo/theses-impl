# Routers - FastAPI Route Handlers

## Overview

The `routers/` directory contains FastAPI APIRouter instances that group related endpoints. These routers are included in the main application via `app.include_router()`.

## Contents

| File | Description |
|------|-------------|
| `admin.py` | Admin-only endpoints for user and system management |
| `__init__.py` | Package initialization |

## Admin Router

### Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/admin/users` | List all users with progress metrics | Admin |
| GET | `/admin/users/{user_id}` | Get detailed user information | Admin |
| PUT | `/admin/users/{user_id}/status` | Activate or deactivate user account | Admin |
| PUT | `/admin/users/{user_id}/role` | Change user role (user/admin) | Admin |
| GET | `/admin/settings` | Get system settings (read-only) | Admin |
| GET | `/admin/stats` | Get system-wide statistics | Admin |

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

## Business Logic

### User Management

- **List users**: Returns all users with computed progress metrics (conversation count, assessment stats)
- **User status**: Admins cannot deactivate their own account (self-protection)
- **Role change**: Admins cannot change their own role (prevents lockout)

### Statistics

System stats are computed in real-time from the database:
- Total and active user counts
- Conversation and assessment totals
- Average assessment scores (excluding ungraded)

### Security

All admin endpoints require:
1. Valid JWT token
2. User role = `admin`

Enforced via `Depends(get_current_admin_user)` dependency.

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
