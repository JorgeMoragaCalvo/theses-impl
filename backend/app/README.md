# App – Main Application Module

## Overview

The `app/` directory contains the core FastAPI application for the AI Tutoring System. It includes the main entry point, configuration, database models, authentication, and organizes the business logic into agents, services, routers, and tools.

## Contents

| File          | Description                                                      |
|---------------|------------------------------------------------------------------|
| `main.py`     | FastAPI application entry point with all endpoints (~908 lines)  |
| `config.py`   | Environment-based configuration using Pydantic BaseSettings      |
| `database.py` | SQLAlchemy ORM models and session management                     |
| `auth.py`     | JWT authentication and password hashing                          |
| `models.py`   | Pydantic request/response schemas                                |
| `utils.py`    | Utility functions for message formatting and confusion detection |
| `__init__.py` | Package initialization                                           |

| Directory   | Description                                          |
|-------------|------------------------------------------------------|
| `agents/`   | AI tutoring agents for different optimization topics |
| `api/`      | API extensions (placeholder for future use)          |
| `routers/`  | FastAPI route handlers (admin routes)                |
| `services/` | Business logic services                              |
| `tools/`    | LangChain tools for agent capabilities               |

## Request Flow

```diagram
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Client    │────▶│   main.py    │────▶│  auth.py        │
│   Request   │     │   Endpoint   │     │  (JWT verify)   │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                  │
                           ┌───────────────────────▼───────────────────────┐
                           │              Service Layer                    │
                           │  ┌────────────────┐  ┌─────────────────────┐  │
                           │  │ Conversation   │  │ Assessment Service  │  │
                           │  │ Service        │  │                     │  │
                           │  └───────┬────────┘  └──────────┬──────────┘  │
                           │          │                      │             │
                           │  ┌───────▼────────┐  ┌──────────▼──────────┐  │
                           │  │  LLM Service   │◀─│   Grading Service   │  │
                           │  └───────┬────────┘  └─────────────────────┘  │
                           └──────────┼────────────────────────────────────┘
                                      │
                           ┌──────────▼──────────┐
                           │    Agents Layer     │
                           │  (Topic-specific)   │
                           │  ┌───────────────┐  │
                           │  │  BaseAgent    │  │
                           │  │  + LP/IP/NLP  │  │
                           │  │  + MM/OR      │  │
                           │  └───────┬───────┘  │
                           │          │          │
                           │  ┌───────▼───────┐  │
                           │  │    Tools      │  │
                           │  │ (LangChain)   │  │
                           │  └───────────────┘  │
                           └─────────────────────┘
                                      │
                           ┌──────────▼──────────┐
                           │    database.py      │
                           │    (SQLAlchemy)     │
                           └─────────────────────┘
```

## Core Modules

### main.py

The FastAPI application entry point containing:

- **Application setup**: CORS, lifespan, routers
- **Agent Registry**: Maps topics to agent instances
- **Authentication endpoints**: `/auth/register`, `/auth/login`, `/auth/me`
- **Student endpoints**: CRUD operations and progress tracking
- **Chat endpoint**: Core tutoring interaction
- **Conversation endpoints**: History retrieval
- **Assessment endpoints**: Generation, submission, grading
- **Exercise endpoints**: Pre-built exercise management
- **Admin endpoints**: Included via router

### config.py

Environment-based configuration:

```python
# Key settings
LLM_PROVIDER      # gemini, openai, or anthropic
DATABASE_URL      # PostgreSQL connection string
SECRET_KEY        # JWT signing key
TEMPERATURE       # LLM temperature (default: 0.4)
MAX_TOKENS        # LLM max tokens (default: 2000)
```

### database.py

SQLAlchemy ORM models:

| Model          | Purpose                                            |
|----------------|----------------------------------------------------|
| `Student`      | User profile with knowledge levels and preferences |
| `Conversation` | Chat session with topic and metadata               |
| `Message`      | Individual messages with agent info                |
| `Assessment`   | Questions, answers, grading                        |
| `Feedback`     | User feedback on responses                         |

Enums:
- `KnowledgeLevel`: beginner, intermediate, advanced
- `Topic`: operations_research, mathematical_modeling, linear_programming, integer_programming, nonlinear_programming
- `UserRole`: user, admin
- `GradingSource`: auto, admin

### auth.py

Authentication features:
- JWT token creation and validation (HS256, 7-day expiry)
- Password hashing with bcrypt (72-byte limit handling)
- Role-based access control dependencies
- `get_current_user` and `get_current_admin_user` dependencies

### models.py

Pydantic schemas for:
- Student create/update/response
- Chat request/response
- Assessment generation/submission/grading
- Conversation and message responses
- Feedback creation
- Health check response

### utils.py

Utility functions:
- `format_conversation_history()` - Format messages for LLM
- `detect_confusion_signals()` - Detect student confusion
- `detect_repeated_topic()` - Find repeated questions
- `format_knowledge_level_context()` - Knowledge level descriptions
- `should_request_feedback()` - Determine feedback timing
- `format_error_message()` - User-friendly error messages

## Business Logic

### Agent Selection

The `AGENT_REGISTRY` in `main.py` maps topics to agents:

```python
AGENT_REGISTRY = {
    "operations_research": get_operations_research_agent,
    "linear_programming": get_linear_programming_agent,
    "mathematical_modeling": get_mathematical_modeling_agent,
    "nonlinear_programming": get_nonlinear_programming_agent,
    "integer_programming": get_integer_programming_agent
}
```

### Knowledge Level Tracking

Each student has knowledge levels per topic stored as JSON:

```python
knowledge_levels = {
    "operations_research": "beginner",
    "mathematical_modeling": "beginner",
    "linear_programming": "beginner",
    "integer_programming": "beginner",
    "nonlinear_programming": "beginner"
}
```

### Adaptive Learning

The system adapts responses based on:
1. Student knowledge level
2. Detected confusion signals
3. Previously used explanation strategies
4. Repeated topic detection

## Usage

### Starting the Application

```python
# Direct run
python -m app.main

# Or via uvicorn
uvicorn app.main:app --reload
```

### Adding New Endpoints

1. For grouped routes, add to `routers/` and include in `main.py`
2. For single endpoints, add directly to `main.py`
3. Use dependency injection for auth: `Depends(get_current_user)`

### Configuration Override

```python
# Override settings programmatically
from app.config import settings
settings.temperature = 0.7
```

## Changelog

- **v1.0.0** (2026-01-05): Initial documentation
- **v1.1.0** (2026-02-03): Added some tools, exercise features, basic user restrictiveness to `@usach` domain
- **v1.1.1** (2026-02-07): New exercises were added.