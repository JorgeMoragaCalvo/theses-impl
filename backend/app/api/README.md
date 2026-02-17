# API - API Extensions

## Overview

The `api/` directory is a placeholder for future API extensions and versioning support. Currently, it contains only the package initialization file.

## Contents

| File          | Description                    |
|---------------|--------------------------------|
| `__init__.py` | Package initialization (empty) |

## Business Logic

This directory is reserved for:
- API versioning (e.g., `v1/`, `v2/` subdirectories)
- API-specific middleware
- OpenAPI schema customizations
- Rate limiting configurations
- API key management

## Future Usage

### API Versioning

```diagram
api/
├── __init__.py
├── v1/
│   ├── __init__.py
│   ├── endpoints.py
│   └── schemas.py
└── v2/
    ├── __init__.py
    ├── endpoints.py
    └── schemas.py
```

### Middleware

```python
# api/middleware.py
from fastapi import Request

async def api_logging_middleware(request: Request, call_next):
    # Log API requests
    response = await call_next(request)
    return response
```

## Usage

Currently, all endpoints are defined directly in `main.py`. When the API grows, endpoints can be migrated here for better organization.

## Changelog

- **v1.0.0** (2026-01-05): Initial documentation
- **v1.1.0** (2026-02-03): Added some tools, exercise features, basic user restrictiveness to `@usach` domain
- **v1.1.1** (2026-02-07): New exercises were added.
- **v1.2.1** (2026-02-13): New functionality for locked and unlocked exercises.
- **v1.3.1** (2026-02-16): Added concept-level mastery tracking — when assessments are graded.