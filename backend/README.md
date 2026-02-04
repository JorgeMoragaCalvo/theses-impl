# Backend - AI Tutoring System for Optimization Methods

## Overview

This is the backend API for an AI-powered tutoring system that helps students learn optimization methods. The system provides personalized, adaptive learning experiences through specialized AI agents for different optimization topics.

## Architecture

```diagram
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Application                      │
├─────────────────────────────────────────────────────────────────┤
│  Routers (admin.py)  │  Main Endpoints (main.py)                │
├──────────────────────┼──────────────────────────────────────────┤
│                      │                                          │
│   ┌──────────────────▼──────────────────┐                       │
│   │            Services Layer           │                       │
│   │  ┌─────────────┐ ┌────────────────┐ │                       │
│   │  │ LLMService  │ │ Conversation   │ │                       │
│   │  │             │ │ Service        │ │                       │
│   │  └─────────────┘ └────────────────┘ │                       │
│   │  ┌─────────────┐ ┌────────────────┐ │                       │
│   │  │ Assessment  │ │ Grading        │ │                       │
│   │  │ Service     │ │ Service        │ │                       │
│   │  └─────────────┘ └────────────────┘ │                       │
│   └──────────────────┬──────────────────┘                       │
│                      │                                          │
│   ┌──────────────────▼──────────────────┐                       │
│   │             Agents Layer            │                       │
│   │  ┌─────────┐ ┌─────────┐ ┌────────┐ │                       │
│   │  │   LP    │ │   IP    │ │  NLP   │ │                       │
│   │  │  Agent  │ │  Agent  │ │ Agent  │ │                       │
│   │  └─────────┘ └─────────┘ └────────┘ │                       │
│   │  ┌─────────┐ ┌─────────────────────┐│                       │
│   │  │   MM    │ │        OR           ││                       │
│   │  │  Agent  │ │       Agent         ││                       │
│   │  └─────────┘ └─────────────────────┘│                       │
│   └──────────────────┬──────────────────┘                       │
│                      │                                          │
│   ┌──────────────────▼──────────────────┐                       │
│   │              Tools Layer            │                       │
│   │  ┌─────────────┐ ┌────────────────┐ │                       │
│   │  │  Modeling   │ │    OR Tools    │ │                       │
│   │  │   Tools     │ │                │ │                       │
│   │  └─────────────┘ └────────────────┘ │                       │
│   └─────────────────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PostgreSQL Database                         │
│  Students │ Conversations │ Messages │ Assessments │ Feedback   │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| LLM Integration | LangChain |
| LLM Providers | OpenAI, Anthropic, Google Gemini |
| Authentication | JWT (HS256) |
| Password Hashing | Bcrypt |

## Directory Structure

```diagram
backend/
├── app/
│   ├── agents/           # AI tutoring agents (LP, IP, NLP, MM, OR)
│   ├── api/              # API extensions (placeholder)
│   ├── routers/          # FastAPI route handlers
│   ├── services/         # Business logic services
│   ├── tools/            # Agent tools
│   │   ├── modeling_tools/   # Mathematical modeling tools
│   │   └── or_tools/         # Operations research tools
│   ├── __init__.py
│   ├── auth.py           # JWT authentication & password handling
│   ├── config.py         # Environment-based configuration
│   ├── database.py       # SQLAlchemy ORM models & session management
│   ├── main.py           # FastAPI application entry point
│   ├── models.py         # Pydantic request/response models
│   └── utils.py          # Utility functions
├── init_db.py            # Database initialization script
├── reset_db.py           # Database reset script
└── README.md             # This file
```

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL database
- API key for at least one LLM provider (OpenAI, Anthropic, or Google)

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/tutoring_db

# LLM Provider (choose one: gemini, openai, anthropic)
LLM_PROVIDER=gemini

# API Keys (set the one matching your provider)
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Security
SECRET_KEY=your_secret_key_here

# Optional
DEBUG=false
LOG_LEVEL=INFO
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Run the application
uvicorn app.main:app --reload
```
<details>
  <summary><b>API Endpoints</b></summary>

#### Authentication
| Method | Endpoint         | Description             |
|--------|------------------|-------------------------|
| POST   | `/auth/register` | Register new user       |
| POST   | `/auth/login`    | Login and get JWT token |
| GET    | `/auth/me`       | Get current user info   |

#### Students
| Method | Endpoint                       | Description               |
|--------|--------------------------------|---------------------------|
| POST   | `/students`                    | Create student profile    |
| GET    | `/students/{id}`               | Get student by ID         |
| PUT    | `/students/{id}`               | Update student profile    |
| GET    | `/students`                    | List all students         |
| GET    | `/students/{id}/progress`      | Get student progress      |
| GET    | `/students/{id}/conversations` | Get student conversations |
| GET    | `/students/{id}/assessments`   | Get student assessments   |

#### Chat
| Method | Endpoint              | Description                      |
|--------|-----------------------|----------------------------------|
| POST   | `/chat`               | Send message and get AI response |
| GET    | `/conversations/{id}` | Get conversation with messages   |

#### Assessments
| Method | Endpoint                              | Description                      |
|--------|---------------------------------------|----------------------------------|
| POST   | `/assessments/generate`               | Generate personalized assessment |
| POST   | `/assessments/generate/from-exercise` | Generate from pre-built exercise |
| GET    | `/assessments/{id}`                   | Get assessment details           |
| POST   | `/assessments/{id}/submit`            | Submit answer (auto-grades)      |
| POST   | `/assessments/{id}/grade`             | Admin grade/override             |

#### Exercises
| Method | Endpoint          | Description              |
|--------|-------------------|--------------------------|
| GET    | `/exercises`      | List available exercises |
| GET    | `/exercises/{id}` | Get exercise preview     |

#### Admin (requires admin role)
| Method | Endpoint                   | Description              |
|--------|----------------------------|--------------------------|
| GET    | `/admin/users`             | List users with progress |
| GET    | `/admin/users/{id}`        | Get user details         |
| PUT    | `/admin/users/{id}/status` | Activate/deactivate user |
| PUT    | `/admin/users/{id}/role`   | Change user role         |
| GET    | `/admin/settings`          | Get system settings      |
| GET    | `/admin/stats`             | Get system statistics    |

#### System
| Method | Endpoint    | Description                 |
|--------|-------------|-----------------------------|
| GET    | `/`         | Root endpoint with API info |
| GET    | `/health`   | Health check                |
| POST   | `/feedback` | Submit feedback on message  |
  
</details>

<details>
  <summary><b>Business Logic</b></summary>
  
  #### Adaptive Learning Flow

1. **User sends message** → `/chat` endpoint
2. **Agent selection** → Based on topic (LP, IP, NLP, MM, OR)
3. **Confusion detection** → Analyzes message for confusion signals
4. **Strategy selection** → Chooses explanation strategy based on:
   - Student knowledge level
   - Confusion level detected
   - Previously used strategies
5. **Response generation** → LLM generates adaptive response
6. **Context update** → Conversation history and progress updated

#### Assessment Flow

1. **Generate assessment** → Based on topic, difficulty, and conversation context
2. **Student submits answer** → Answer stored
3. **Auto-grading** → LLM grades against rubric
4. **Admin override** → Optional manual grade adjustment

#### Supported Topics

- Operations Research (general concepts)
- Mathematical Modeling (problem formulation)
- Linear Programming (LP)
- Integer Programming (IP)
- Nonlinear Programming (NLP)
  
</details>

## Running the Application

### Development

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once running, access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Changelog

- **v1.0.0** (2026-01-05): Initial documentation
- **v1.1.0** (2026-02-03): Added some tools, exercise features, basic user restrictiveness to `@usach` domain
