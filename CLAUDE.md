# Project: Multi-Agent Tutoring System

Adaptive AI tutoring system for Operations Research / Mathematical Optimization courses.
Spanish-language UI. Thesis project.

> New to the codebase? Start with [`ONBOARDING.md`](ONBOARDING.md) — a junior-engineer’s guide with the request-flow mental model, glossary, a 3-day reading path, and the data-model ER diagram.

## Project Structure

```
backend/app/
  main.py              - FastAPI app, lifespan, middleware/CORS, router registration, /health & / endpoints
  config.py            - Settings via pydantic-settings (loads .env)
  enums.py             - Shared enums (KnowledgeLevel, Topic, MessageRole, UserRole, GradingSource, MasteryLevel, EventCategory)
  database.py          - SQLAlchemy models, engine, session (Student, Conversation, Message, Assessment, Feedback, StudentCompetency, ConceptHierarchy, ReviewSession, ActivityEvent)
  models.py            - Pydantic request/response schemas
  auth.py              - JWT auth, password hashing, get_current_user/get_current_admin_user
  utils.py             - Confusion detection, strategy helpers, error formatting
  rate_limit.py        - slowapi limiter + rate-limit-exceeded handler

  routers/             - HTTP route definitions, one router per resource (registered in main.py)
    chat.py            - /chat endpoint + AGENT_REGISTRY + get_agent_for_topic; conversation endpoints
    auth.py            - Login/register/token
    students.py        - Student profile endpoints
    assessments.py     - Assessment generation/submission
    exercises.py       - Pre-built exercise endpoints
    competencies.py    - Concept mastery endpoints
    reviews.py         - Spaced-repetition review endpoints
    feedback.py        - Message feedback endpoints
    analytics.py       - Activity analytics endpoints
    admin.py           - Admin dashboard endpoints

  agents/
    base_agent.py      - ABC with adaptive learning: confusion detection, strategy selection, feedback requests, spaced repetition context
    linear_programming_agent.py
    integer_programming_agent.py
    nlp_agent.py       - Nonlinear programming (file is named nlp_agent.py; there is no nonlinear_programming_agent.py file, though its registry getter is named get_nonlinear_programming_agent)
    mathematical_modeling_agent.py
    operations_research_agent.py

  services/
    llm_service.py           - LangChain adapter for Gemini/OpenAI/Anthropic, tool-calling loop
    conversation_service.py  - Conversation CRUD, context building
    assessment_service.py    - LLM-generated assessments
    exercise_assessment_service.py - Pre-built exercise registry from data/course_materials/
    exercise_manager.py      - Loads exercise files from disk
    exercise_progress_service.py
    grading_service.py       - Auto-grading via LLM
    llm_response_parser.py   - JSON parsing from LLM output
    competency_service.py    - Concept mastery tracking (Bloom taxonomy)
    bkt_service.py           - Bayesian Knowledge Tracing posterior (bkt_p_learn)
    spaced_repetition_service.py - SM-2 algorithm for review scheduling
    affect_service.py        - Infers engagement/frustration from activity events
    analytics_service.py     - Activity event aggregation for admin dashboard

  tools/
    spaced_repetition_tool.py - SpacedRepetitionReviewTool (BaseTool) - starts/fetches SM-2 review sessions; used by agents via tool-calling
    modeling_tools/          - LangChain tools for LP/MM agents
      problem_solver.py      - SciPy/PuLP solver
      region_visualizer.py   - Matplotlib feasible region plots
      model_validator.py     - Formulation validation
      exercise_validator.py  - Exercise solution checking
      exercise_practice.py   - Practice problem generation
    or_tools/
      problem_classifier.py  - Problem type classification
      timeline_explorer.py   - OR history timeline

frontend/                    - Streamlit multi-page app
  app.py                     - Home/auth page
  pages/
    1_chat.py                - Chat interface (topic selection, conversation)
    2_assessment.py          - Assessment generation and submission
    3_progress.py            - Student progress/metrics
    4_admin.py               - Admin dashboard (users, stats, analytics)
  utils/
    api_client.py            - Singleton HTTP client, JWT injection, auto-logout on 401
    constants.py             - UI constants
    activity_tracker.py      - Frontend analytics event tracking
    idle_detector.py         - Idle detection for session analytics

data/course_materials/       - Pre-built exercises (statement.md + model.md per exercise)
  linear_programming/exercises/lp_01..lp_06/
  integer_programming/exercises/ip_01..ip_06/
  non_lineal_programming/exercises/nlp_01..nlp_08/
  mathematical_modeling/exercises/mm_01..mm_10/
  operations_research/exercises/or_01..or_06/
```

## Tech Stack & Decisions

- **Python 3.13**, FastAPI 0.120, Streamlit 1.50
- **LLM**: LangChain abstraction over Gemini (default), OpenAI, Anthropic. Configured via `LLM_PROVIDER` env var. Tool-calling supported.
- **Database**: PostgreSQL via SQLAlchemy 2.0 (no Alembic yet, uses `create_all`)
- **Auth**: JWT tokens via python-jose, bcrypt passwords, role-based (USER/ADMIN)
- **Agents**: five specialist agents inheriting `BaseAgent`. Each has a custom system prompt, available strategies, and optional LangChain tools. Agents selected via `AGENT_REGISTRY` dict in main.py.
- **Adaptive learning**: Confusion detection (keyword analysis), explanation strategy selection (seven strategies), feedback request injection, spaced repetition (SM-2)
- **Competency tracking**: Bloom taxonomy concept hierarchy per topic, mastery scores, spaced repetition scheduling
- **Grading**: LLM-based auto-grading with admin override. Max score 7.0 (Chilean scale).
- **UI language**: Spanish
- **Code style**: ruff (E, W, F, I, B, UP rules), double quotes, spaces. No mypy configured.
- **Enums**: defined once in `enums.py`, re-exported from `database.py` and `models.py` for backwards compatibility
- **No foreign keys** in SQLAlchemy models (student_id, conversation_id are plain Integer columns)
- **JSON columns** for flexible data: knowledge_levels, preferences, extra_data

## Deployment Summary                                                                                                                                                                                  
                                                                                                                                                                               
5 Blocking Issues                                                                                                                                                                 
Most urgent action: rotate the exposed API keys immediately (they're in git history), then set DEBUG=false, and generate a real SECRET_KEY. The test suite is the longest-lead item — the fixtures in conftest.py are already well-designed, you need actual test files.

| # | Issue                                 | Detail                                                                                                                                                    |
|---|---------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | SECRET_KEY is the placeholder  string | .env:39 has your-secret-key-change-this-in-production-min-32-chars. The validation in config.py only rejects it when DEBUG=false, so it slips through now |
| 2 | DEBUG=true in .env                    | Disables the secret key check, exposes stack traces, and triggers wildcard CORS.                                                                          |
| 3 | CORS is ["*"]                         | Because CORS_ORIGINS is empty and DEBUG=true, main.py falls back to allowing all origins.                                                                 |
| 4 | No database SSL                       | database.py engine has no sslmode — connections are unencrypted.                                                                                          |
| 5 | /metrics unauthenticated              | By design per the code comment — needs to be blocked at the reverse proxy/firewall level.                                                                 |

---
High Priority (before public traffic)
- No database SSL (sslmode=require missing from DATABASE_URL)
- All frontend pages fall back to http://localhost:8000 if BACKEND_URL is not set
- /metrics endpoint is unauthenticated — leaks system info
- Pool size is too small for concurrent users (pool_size=5)

---
What's Already Production-Quality

The infrastructure is solid: multi-stage Docker builds, non-root containers, Nginx with HTTPS + HSTS + TLS 1.2+, rate limiting, Gunicorn/UvicornWorker, bcrypt passwords, JWT expiration, Prometheus metrics, and GitHub Actions CI with pip-audit and CodeQL.

---

To deploy, the minimum actions are:
1. Generate a real secret key: python -c "import secrets; print(secrets.token_urlsafe(32))" and set it in .env
2. Set DEBUG=false in .env
3. Set CORS_ORIGINS=https://your-domain.com in .env
4. Add ?sslmode=require to DATABASE_URL in .env
5. Block /metrics at the Nginx/reverse proxy level

The database is handled — docker-compose includes a postgres:16-alpine service (db), and the backend connects to it via @db:5432 (the Docker internal hostname), not localhost. So when you deploy with docker-compose up, PostgreSQL is spun up automatically alongside the app.
                                                                                                                                                                                    
Two things are still worth noting:                                                                                                                                                    
1. DATABASE_URL in your .env points to localhost:5432 — that's fine for local dev, but when running via Docker Compose, the correct URL (@db:5432/...) is injected automatically by the compose file, overriding .env. So this is not a problem in practice.
2. No Alembic migrations — the app uses create_all() on startup, which creates tables on the first run. This is fine for initial deployment. If you later change the schema (add a column, rename a table), you'll need to handle that manually or add Alembic. Not a blocker now, but worth knowing.

So the database itself is fine for deployment — PostgreSQL is bundled in the compose file, and the connection string is set correctly there.