# Product Requirements Document (PRD)

## Multi-Agent Adaptive Tutoring System for Operations Research

**Version:** 1.6.4
**Date:** March 2026
**Author:** Jorge Moraga Calvo
**Type:** Thesis Project — Universidad de Santiago de Chile (USACH)

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Problem Statement](#2-problem-statement)
3. [Target Users](#3-target-users)
4. [System Architecture](#4-system-architecture)
5. [Feature Specification](#5-feature-specification)
   - 5.1 [Authentication & Authorization](#51-authentication--authorization)
   - 5.2 [Multi-Agent Tutoring System](#52-multi-agent-tutoring-system)
   - 5.3 [Adaptive Learning Engine](#53-adaptive-learning-engine)
   - 5.4 [Assessment & Grading](#54-assessment--grading)
   - 5.5 [Exercise System](#55-exercise-system)
   - 5.6 [Competency Tracking](#56-competency-tracking)
   - 5.7 [Spaced Repetition](#57-spaced-repetition)
   - 5.8 [Analytics & Admin Dashboard](#58-analytics--admin-dashboard)
   - 5.9 [Agent Tools](#59-agent-tools)
6. [Data Model](#6-data-model)
7. [API Specification](#7-api-specification)
8. [User Interface](#8-user-interface)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [Configuration](#10-configuration)

---

## 1. Product Overview

An adaptive AI-powered tutoring system designed for university-level Operations Research and Mathematical Optimization courses. The system employs five specialist AI agents — each covering a distinct optimization discipline — that adapt their teaching strategies in real time based on detected student confusion, knowledge level, and learning history.

The platform provides conversational tutoring, personalized assessments, pre-built exercises with progression gating, competency tracking based on Bloom's taxonomy, and spaced repetition scheduling — all through a Spanish-language interface.

### Key Differentiators

- **Multi-agent specialization** — dedicated agents for each OR topic, each with domain-specific system prompts, strategies, and tools
- **Real-time adaptive learning** — confusion detection, dynamic strategy selection, and feedback injection within conversations
- **Competency-driven progression** — Bloom taxonomy concept hierarchies with prerequisite-aware recommendations
- **Spaced repetition integration** — SM-2 algorithm scheduling review sessions based on mastery decay
- **Multi-provider LLM abstraction** — supports Gemini, OpenAI, and Anthropic via LangChain with tool-calling

---

## 2. Problem Statement

Operations Research courses involve abstract mathematical concepts (linear programming, integer optimization, nonlinear methods) that students often struggle to internalize through traditional instruction alone. Common pain points include:

- Difficulty translating real-world problems into mathematical formulations
- Lack of personalized feedback on formulation attempts
- No adaptive pacing — all students receive the same material regardless of mastery
- Limited access to one-on-one tutoring outside class hours
- No systematic review scheduling to reinforce learned concepts

This system addresses these gaps by providing an always-available, adaptive AI tutor that detects confusion, adjusts explanation strategies, tracks competency at the concept level, and schedules reviews to optimize long-term retention.

---

## 3. Target Users

### 3.1 Students (Primary Users)

University students enrolled in Operations Research or Mathematical Optimization courses. They interact with the system to:

- Receive tutoring on specific topics through conversational AI
- Practice with pre-built exercises and AI-generated assessments
- Track their progress across topics and concepts
- Review concepts through spaced repetition sessions

### 3.2 Administrators / Instructors

Course instructors or teaching assistants who:

- Manage user accounts (activation, role assignment)
- Override auto-graded assessment scores
- Monitor student engagement and learning analytics
- View system-wide statistics and usage patterns

---

## 4. System Architecture

### High-Level Architecture

```diagram
┌─────────────────────────────────────────────────────┐
│                  Frontend (Streamlit)               │
│  ┌──────┐ ┌──────┐ ┌──────────┐ ┌────────┐ ┌─────┐  │
│  │ Home │ │ Chat │ │Assessment│ │Progress│ │Admin│  │
│  └──────┘ └──────┘ └──────────┘ └────────┘ └─────┘  │
│                        │                            │
│              API Client (JWT Auth)                  │
└────────────────────────┬────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────┴────────────────────────────┐
│                  Backend (FastAPI)                  │
│                                                     │
│  ┌─────────────────────────────────────────────┐    │
│  │              Agent Registry                 │    │
│  │  ┌────┐ ┌────┐ ┌─────┐ ┌────┐ ┌──────────┐  │    │
│  │  │ LP │ │ IP │ │ NLP │ │ MM │ │    OR    │  │    │
│  │  └──┬─┘ └──┬─┘ └──┬──┘ └──┬─┘ └────┬─────┘  │    │
│  │     └──────┴──────┴──────┴────────┘         │    │
│  │              BaseAgent (ABC)                │    │
│  │   confusion detection · strategy selection  │    │
│  │   feedback injection · spaced rep context   │    │
│  └─────────────────────┬───────────────────────┘    │
│                        │                            │
│  ┌─────────────────────┴───────────────────────┐    │
│  │             Services Layer                  │    │
│  │  LLM · Conversation · Assessment · Grading  │    │
│  │  Exercise · Competency · SpacedRepetition   │    │
│  │  Analytics · ResponseParser                 │    │
│  └─────────────────────┬───────────────────────┘    │
│                        │                            │
│  ┌─────────────────────┴───────────────────────┐    │
│  │          LangChain Tool Layer               │    │
│  │  ProblemSolver · RegionVisualizer           │    │
│  │  ModelValidator · ExerciseValidator         │    │
│  │  ExercisePractice · ProblemClassifier       │    │
│  │  TimelineExplorer                           │    │
│  └─────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              │    PostgreSQL DB    │
              └─────────────────────┘
```

### Tech Stack

| Layer                | Technology                                    |
|----------------------|-----------------------------------------------|
| Frontend             | Streamlit 1.50, Altair charts                 |
| Backend              | FastAPI 0.120, Uvicorn                        |
| LLM Integration      | LangChain 1.0.5 (Gemini / OpenAI / Anthropic) |
| Database             | PostgreSQL, SQLAlchemy 2.0                    |
| Auth                 | JWT (python-jose), bcrypt                     |
| Optimization Solvers | SciPy (linprog, milp)                         |
| Visualization        | Matplotlib (feasible region plots)            |
| Language             | Python 3.13                                   |

---

## 5. Feature Specification

### 5.1 Authentication & Authorization

#### Registration

- Email/password registration with a minimum 8-character password
- **Domain-based auto-activation**: `@usach.cl` emails are automatically activated; all others require admin approval
- Pending registrations display a status message to the user

#### Login

- JWT-based authentication with HS256 algorithm
- Tokens expire after 7 days
- Bearer token transmitted via Authorization header
- Frontend persists tokens in Streamlit session state and browser localStorage

#### Authorization

| Role               | Capabilities                                                                  |
|--------------------|-------------------------------------------------------------------------------|
| **User (Student)** | Chat, assessments, exercises, view own progress                               |
| **Admin**          | All user capabilities + user management, analytics dashboard, grade overrides |

- Users can only access their own profiles and conversations
- Admins can view/manage any user
- Self-deactivation is prevented

#### Password Security

- bcrypt hashing with 72-byte UTF-8 informed truncation
- Secure password verification with byte-level truncation handling

---

### 5.2 Multi-Agent Tutoring System

Five specialist agents, each inheriting from `BaseAgent`, are routed by a topic:

| Agent                     | Topic                   | Key Areas                                                                            | Tools                                                                                |
|---------------------------|-------------------------|--------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| **Linear Programming**    | `linear_programming`    | Formulation, graphical method, simplex, duality, sensitivity analysis                | —                                                                                    |
| **Integer Programming**   | `integer_programming`   | IP formulation, binary variables, branch & bound, cutting planes, MIP                | —                                                                                    |
| **Nonlinear Programming** | `nlp_agent`             | Unconstrained/constrained optimization, KKT conditions, convexity, numerical methods | —                                                                                    |
| **Mathematical Modeling** | `mathematical_modeling` | Problem formulation, decision variables, objectives, constraints, model selection    | ModelValidator, ProblemSolver, RegionVisualizer, ExercisePractice, ExerciseValidator |
| **Operations Research**   | `operations_research`   | OR methodology, problem classification, decision frameworks                          | ProblemClassifier, TimelineExplorer                                                  |

#### Agent Capabilities

- **Dynamic system prompts** — adapted per student knowledge level (beginner / intermediate / advanced) with level-specific examples and guidance
- **Topic validation** — agents verify message relevance and redirect off-topic queries
- **Course materials integration** — agents load topic-specific Markdown content from `data/course_materials/`
- **Conversation context** — agents receive full conversation history, student profile, assessment history, and competency data
- **Tool-calling** — agents with tools execute a LangChain tool-calling loop (max three iterations) to solve, visualize, or validate problems

#### Agent Selection

Topic-based routing via `AGENT_REGISTRY` dictionary in `main.py`. Fallback to Linear Programming agent if a topic is not found.

---

### 5.3 Adaptive Learning Engine

The adaptive learning system operates across four dimensions:

#### 5.3.1 Confusion Detection

- **Keyword analysis** — scans student messages for confusion signals (e.g., "no entiendo", "estoy confundido")
- **Repetition tracking** — monitors repeated questions on the same topic across conversation history
- **Confusion levels**: `none`, `low`, `medium`, `high`
- **Escalation rules**: 3+ repetitions of the same topic trigger medium confusion

#### 5.3.2 Explanation Strategy Selection

Seven core strategies, selected based on confusion level, knowledge level, and usage history:

| Strategy                                    | Description                             |
|---------------------------------------------|-----------------------------------------|
| **Paso a paso** (Step-by-step)              | Decomposed procedural walkthrough       |
| **Basado en ejemplos** (Example-based)      | Concrete worked examples                |
| **Conceptual**                              | High-level conceptual explanation       |
| **Analógico** (Analogy-based)               | Real-world analogies                    |
| **Visual**                                  | Diagrams, plots, visual representations |
| **Matemático-formal** (Formal-mathematical) | Rigorous mathematical treatment         |
| **Comparativo** (Comparative)               | Contrasting approaches or methods       |

Each agent defines its own subset of available strategies. Selection logic:
- High confusion → the simplest strategies (step-by-step, examples)
- Strategy rotation to avoid repetition
- Previously successful strategies are weighted higher
- Strategy effectiveness is tracked per conversation

#### 5.3.3 Adaptive Prompt Injection

Dynamic system prompt assembly:
1. Base system prompt (agent identity and scope)
2. Adaptive teaching mode (confusion-specific instructions + selected strategy)
3. Spaced repetition context (due review reminders)

Visual markers in prompts: ⚠️ high confusion, 📌 medium, 💡 low

#### 5.3.4 Feedback Request Injection

- Automatic "understanding checks" appended to agent responses
- Different prompts by confusion level (more supportive for high confusion)
- Offers alternative explanation paths when confusion is detected
- Context-aware: considers response length and conversation patterns

---

### 5.4 Assessment & Grading

#### LLM-Generated Assessments

- Personalized assessment generation that considers:
  - Student knowledge level and identified gaps
  - Recent conversation topics
  - Assessment history and scores
  - Strategy effectiveness data
- Three difficulty levels: Beginner, Intermediate, Advanced
- Topic-specific generation guidelines for each of the five topics
- Output: question, correct answer, rubric

#### Auto-Grading

- LLM-based rubric evaluation producing:
  - Score on the 1.0 – 7.0 scale (Chilean grading system)
  - Detailed Spanish-language feedback
  - Identified concepts tested
- Partial credit for correct methodology with a wrong answer
- Competency updates triggered on grading (≥60% = correct)
- Spaced repetition scheduling triggered on first grading
- Fallback parsing for malformed LLM responses

#### Admin Grade Override

- Administrators can override any auto-graded assessment
- Override records the grading source as `admin` with timestamp
- Feedback and score can both be modified

#### Student Feedback on Responses

- Students can rate agent responses (1–5 scale)
- Helpfulness flag (boolean)
- Free-text comment
- Stored per message for analysis

---

### 5.5 Exercise System

#### Exercise Library

41 pre-built exercises across 5 topics:

| Topic                 | Count | IDs             |
|-----------------------|-------|-----------------|
| Linear Programming    | 6     | lp_01 – lp_06   |
| Integer Programming   | 6     | ip_01 – ip_06   |
| Nonlinear Programming | 9     | nlp_01 – nlp_09 |
| Mathematical Modeling | 14    | mm_01 – mm_13   |
| Operations Research   | 6     | or_01 – or_06   |

Each exercise contains:
- `statement.md` — problem statement
- `model.md` — reference solution/model
- `meta-data.json` — difficulty, rank, tier (Mathematical Modeling exercises)

#### Exercise Modes

1. **Practice (Original)** — exercise presented as-is with a reference solution used for grading
2. **Similar (AI-Generated Variant)** — LLM generates a variation with different context/numbers but the same underlying model type

#### Progression Gating

- Exercises are assigned a rank (difficulty tier)
- Rank 1 exercises are always unlocked
- Rank N+1 unlocks when any Rank N exercise is scored ≥50% of max score
- Unranked exercises (rank=0) are always available
- Per-topic gating (progress in LP does not unlock IP exercises)

#### Exercise Preview

Students see exercise ID, title, model type, difficulty, and tier before starting — but not the solution.

---

### 5.6 Competency Tracking

#### Bloom Taxonomy Concept Hierarchy

- Each topic has a JSON taxonomy file in `data/concept_taxonomies/`
- Concepts organized hierarchically with parent-child relationships
- Bloom levels: Remember → Understand → Apply → Analyze → Evaluate → Create
- Prerequisites defined per concept

#### Mastery Scoring (Exponentially Weighted Average)

```
new_score = α × performance + (1 - α) × old_score
α = 0.3
```

| Mastery Level | Score Threshold | Minimum Attempts |
|---------------|-----------------|------------------|
| MASTERED      | ≥ 0.85          | 5                |
| PROFICIENT    | ≥ 0.60          | 3                |
| DEVELOPING    | ≥ 0.30          | —                |
| NOVICE        | < 0.30          | —                |
| NOT_STARTED   | No attempts     | —                |

#### Prerequisite-Aware Recommendations

- System recommends next concepts to learn based on:
  - Prerequisites all at PROFICIENT or MASTERED level
  - Concept not yet MASTERED
  - Sorted by Bloom level (lower first), then by score
  - Limited to 5 recommendations per query

---

### 5.7 Spaced Repetition

#### SM-2 Algorithm Implementation

- **Initial intervals**: 1, 3, 7, 14, 30, 60 days
- **Default ease factor**: 2.5
- **Minimum ease factor**: 1.3
- **Performance scale**: 0–5 (3+ = passing)

**Successful recall (quality ≥ 3):**
```
ease = ease + [0.1 - (5 - q) × (0.08 + (5 - q) × 0.02)]
interval = initial_intervals[n] or previous_interval × ease
```

**Failed recall (quality < 3):**
```
interval = 1 day
ease = ease - 0.2
```

#### Review Workflow

1. System identifies concepts due for review (`next_review_at ≤ now`)
2. Student starts a review session for a specific concept
3. Student completes the review with a self-assessed performance quality (0–5)
4. System recalculates an ease factor, schedules the next review, and updates mastery score
5. Due reviews are injected into agent context during conversations

---

### 5.8 Analytics & Admin Dashboard

#### Activity Event Tracking

Events captured across 10 categories:

| Category                     | Examples                              |
|------------------------------|---------------------------------------|
| PAGE_VISIT / PAGE_EXIT       | Page navigation with duration         |
| CHAT_MESSAGE                 | Message submissions                   |
| ASSESSMENT_GENERATE / SUBMIT | Assessment lifecycle                  |
| TOPIC_CHANGE                 | Topic selection changes               |
| SESSION_START / SESSION_END  | Browser focus/blur                    |
| IDLE_START / IDLE_END        | Inactivity detection (300s threshold) |
| WIDGET_INTERACTION           | UI element interactions               |

- Events batched (up to 50 per request) and flushed at 10+ event threshold
- JavaScript-based idle detection with mouse/keyboard/scroll/click monitoring
- Session tracking via UUID

#### Admin Dashboard Metrics

| Metric                   | Description                                                                                       |
|--------------------------|---------------------------------------------------------------------------------------------------|
| Daily Active Users       | Distinct students per day                                                                         |
| Average Session Duration | Minutes per session per day                                                                       |
| Peak Usage Hours         | Event distribution by hour                                                                        |
| Page Popularity          | Visit counts and average duration per page                                                        |
| Topic Popularity         | Interaction counts by topic                                                                       |
| User Engagement          | Total events, unique sessions, avg events/session, chat messages, assessments generated/submitted |

All metrics support configurable date ranges (7, 14, 30, 60, 90 days).

#### User Management

- View all users with metrics (conversations, assessments, average score)
- Activate/deactivate accounts
- Assign/revoke admin role
- Self-deactivation prevented

---

### 5.9 Agent Tools

Seven LangChain tools available to agents during conversations:

#### Modeling Tools

| Tool                  | Purpose                                       | Key Details                                                                                                                                                   |
|-----------------------|-----------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **ProblemSolver**     | Solve LP/IP/MIP problems                      | SciPy backend (linprog, milp). Max 20 variables, 50 constraints. Parses linear expressions, reports optimal values, slack, and status.                        |
| **RegionVisualizer**  | Visualize 2D feasible regions                 | Matplotlib plots with constraint lines, shaded feasible region, red corner points, objective direction arrow. Returns base64 PNG (800×600). 2-variable limit. |
| **ModelValidator**    | Validate optimization formulations            | Checks variable names/types/bounds, objective sense/expression, constraint format. Returns errors, warnings, and summary.                                     |
| **ExerciseValidator** | Validate student solutions against references | Parses student and reference markdown. Structural comparison + LLM semantic feedback on variables, objective, constraints, model type.                        |
| **ExercisePractice**  | Interactive exercise browser                  | List exercises, get statements, retrieve hints, reveal solutions.                                                                                             |

#### OR Tools

| Tool                  | Purpose                             | Key Details                                                                                                                        |
|-----------------------|-------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| **ProblemClassifier** | Classify optimization problem types | Detects integer/binary/nonlinear/continuous/network/uncertainty characteristics via keyword analysis. Recommends specialist agent. |
| **TimelineExplorer**  | Explore OR history                  | Queries `data/or_history/timeline.json` for milestones, key figures, and eras. Full-text search across all fields.                 |

---

## 6. Data Model

### Entity Overview

```diagram
Student ──────────< Conversation ──────< Message
   │                     │
   ├──────────< Assessment (optional conv link)
   │
   ├──────────< Feedback
   │
   ├──────────< StudentCompetency ──── ConceptHierarchy
   │
   ├──────────< ReviewSession
   │
   └──────────< ActivityEvent
```

> Note: No foreign key constraints are enforced at the database level. Relationships use plain integer columns.

### Entities

#### Student
| Field                              | Type               | Notes                   |
|------------------------------------|--------------------|-------------------------|
| id                                 | Integer PK         | Auto-increment          |
| name                               | String             |                         |
| email                              | String             | Unique                  |
| password_hash                      | String             | bcrypt                  |
| role                               | Enum (USER, ADMIN) |                         |
| is_active                          | Boolean            | Domain-based activation |
| knowledge_levels                   | JSON               | `{topic: level}`        |
| preferences                        | JSON               | Flexible                |
| created_at, updated_at, last_login | DateTime           |                         |

#### Conversation
| Field                | Type          | Notes                                                   |
|----------------------|---------------|---------------------------------------------------------|
| id                   | Integer PK    |                                                         |
| student_id           | Integer       |                                                         |
| topic                | Enum          | 5 topics                                                |
| started_at, ended_at | DateTime      |                                                         |
| is_active            | Integer (0/1) |                                                         |
| extra_data           | JSON          | strategies_used, confusion_count, successful_strategies |

#### Message
| Field           | Type       | Notes                                                     |
|-----------------|------------|-----------------------------------------------------------|
| id              | Integer PK |                                                           |
| conversation_id | Integer    |                                                           |
| role            | String     | user / assistant / system                                 |
| content         | Text       |                                                           |
| agent_type      | String     | Which agent responded                                     |
| timestamp       | DateTime   |                                                           |
| extra_data      | JSON       | explanation_strategy, confusion_detected, confusion_level |

#### Assessment
| Field                                              | Type               | Notes                           |
|----------------------------------------------------|--------------------|---------------------------------|
| id                                                 | Integer PK         |                                 |
| student_id                                         | Integer            |                                 |
| conversation_id                                    | Integer            | Nullable                        |
| topic                                              | Enum               |                                 |
| question, student_answer, correct_answer, rubric   | Text               |                                 |
| score                                              | Float              | 1.0–7.0 Chilean scale           |
| max_score                                          | Float              | Default 7.0                     |
| feedback                                           | Text               |                                 |
| graded_by                                          | Enum (AUTO, ADMIN) |                                 |
| created_at, submitted_at, graded_at, overridden_at | DateTime           |                                 |
| extra_data                                         | JSON               | difficulty, generation metadata |

#### Feedback
| Field      | Type          | Notes |
|------------|---------------|-------|
| id         | Integer PK    |       |
| message_id | Integer       |       |
| student_id | Integer       |       |
| rating     | Integer       | 1–5   |
| is_helpful | Integer (0/1) |       |
| comment    | Text          |       |
| created_at | DateTime      |       |

#### StudentCompetency
| Field                            | Type       | Notes                           |
|----------------------------------|------------|---------------------------------|
| id                               | Integer PK |                                 |
| student_id                       | Integer    | Indexed                         |
| topic                            | Enum       |                                 |
| concept_id                       | String     | Indexed, unique with student_id |
| concept_name                     | String     |                                 |
| mastery_level                    | Enum       | NOT_STARTED through MASTERED    |
| mastery_score                    | Float      | 0.0–1.0+                        |
| attempts_count, correct_count    | Integer    |                                 |
| decay_factor                     | Float      | SM-2 ease factor                |
| next_review_at                   | DateTime   |                                 |
| last_attempt_at, last_correct_at | DateTime   |                                 |

#### ConceptHierarchy
| Field             | Type       | Notes                |
|-------------------|------------|----------------------|
| id                | Integer PK |                      |
| concept_id        | String     | Unique, indexed      |
| concept_name      | String     |                      |
| topic             | Enum       |                      |
| parent_concept_id | String     | Nullable             |
| bloom_level       | String     | Bloom taxonomy level |
| prerequisites     | JSON       | Array of concept IDs |

#### ReviewSession
| Field                      | Type       | Notes            |
|----------------------------|------------|------------------|
| id                         | Integer PK |                  |
| student_id                 | Integer    |                  |
| concept_id                 | String     |                  |
| assessment_id              | Integer    | Nullable         |
| performance_quality        | Integer    | 0–5 (SM-2 scale) |
| response_time_seconds      | Float      |                  |
| scheduled_at, completed_at | DateTime   |                  |
| next_review_scheduled      | DateTime   |                  |

#### ActivityEvent
| Field            | Type       | Notes         |
|------------------|------------|---------------|
| id               | Integer PK |               |
| student_id       | Integer    |               |
| session_id       | String     | UUID          |
| event_category   | Enum       | 10 categories |
| event_action     | String     |               |
| page_name        | String     |               |
| topic            | String     |               |
| timestamp        | DateTime   | Indexed       |
| duration_seconds | Float      |               |
| extra_data       | JSON       |               |

---

## 7. API Specification

### Authentication

| Method | Endpoint         | Description        | Rate Limit |
|--------|------------------|--------------------|------------|
| POST   | `/auth/register` | Register new user  | 5/min      |
| POST   | `/auth/login`    | Login, receive JWT | 5/min      |
| GET    | `/auth/me`       | Get current user   | —          |

### Students

| Method | Endpoint         | Description            | Auth        |
|--------|------------------|------------------------|-------------|
| POST   | `/students`      | Create student profile | User        |
| GET    | `/students/{id}` | Get student profile    | Owner/Admin |
| PUT    | `/students/{id}` | Update student profile | Owner       |
| GET    | `/students`      | List all students      | User        |

### Chat

| Method | Endpoint                       | Description                    | Rate Limit |
|--------|--------------------------------|--------------------------------|------------|
| POST   | `/chat`                        | Send message to AI tutor       | 10/min     |
| GET    | `/conversations/{id}`          | Get conversation with messages | —          |
| GET    | `/students/{id}/conversations` | List student conversations     | —          |

### Assessments

| Method | Endpoint                              | Description                | Rate Limit |
|--------|---------------------------------------|----------------------------|------------|
| POST   | `/assessments/generate`               | Generate LLM assessment    | 5/min      |
| POST   | `/assessments/generate/from-exercise` | Generate from exercise     | 5/min      |
| GET    | `/assessments/{id}`                   | Get assessment             | —          |
| GET    | `/students/{id}/assessments`          | List student assessments   | —          |
| POST   | `/assessments/{id}/submit`            | Submit answer (auto-grade) | 10/min     |
| POST   | `/assessments/{id}/grade`             | Admin grade override       | Admin      |

### Exercises

| Method | Endpoint              | Description                          |
|--------|-----------------------|--------------------------------------|
| GET    | `/exercises`          | List exercises (filterable by topic) |
| GET    | `/exercises/progress` | Exercises with lock/complete status  |
| GET    | `/exercises/{id}`     | Exercise preview (no solution)       |

### Competency & Progress

| Method | Endpoint                                      | Description                      |
|--------|-----------------------------------------------|----------------------------------|
| GET    | `/students/{id}/progress`                     | Comprehensive progress metrics   |
| GET    | `/students/{id}/competencies`                 | Concept mastery records by topic |
| GET    | `/students/{id}/mastery/{topic}`              | Mastery summary                  |
| GET    | `/students/{id}/recommended-concepts/{topic}` | Next concepts to learn           |

### Spaced Repetition

| Method | Endpoint                       | Description                         |
|--------|--------------------------------|-------------------------------------|
| GET    | `/students/{id}/reviews/due`   | Concepts due for review             |
| POST   | `/students/{id}/reviews/start` | Start review session                |
| POST   | `/reviews/{id}/complete`       | Complete review with quality rating |

### Feedback

| Method | Endpoint    | Description                       |
|--------|-------------|-----------------------------------|
| POST   | `/feedback` | Submit feedback on agent response |

### Analytics

| Method | Endpoint            | Description                            |
|--------|---------------------|----------------------------------------|
| POST   | `/analytics/events` | Record batch of activity events (1–50) |

### Admin

| Method | Endpoint                   | Description                 | Auth  |
|--------|----------------------------|-----------------------------|-------|
| GET    | `/admin/users`             | List all users with metrics | Admin |
| GET    | `/admin/users/{id}`        | Get user details            | Admin |
| PUT    | `/admin/users/{id}/status` | Activate/deactivate user    | Admin |
| PUT    | `/admin/users/{id}/role`   | Update user role            | Admin |
| GET    | `/admin/analytics`         | Analytics summary           | Admin |

### System

| Method | Endpoint  | Description                                     |
|--------|-----------|-------------------------------------------------|
| GET    | `/`       | Root info (version, docs links)                 |
| GET    | `/health` | Health check (DB status, version, LLM provider) |

---

## 8. User Interface

### Pages

| Page           | Route         | Description                                                                |
|----------------|---------------|----------------------------------------------------------------------------|
| **Home**       | `/`           | Authentication (login/register tabs) + inline chat for authenticated users |
| **Chat**       | `/chat`       | Dedicated chat interface with topic selector and conversation history      |
| **Assessment** | `/assessment` | Three tabs: Progress Dashboard, Assessment History, New Assessment         |
| **Progress**   | `/progress`   | Student profile, knowledge levels, conversation history, learning stats    |
| **Admin**      | `/admin`      | Four tabs: User Management, System Stats, Analytics Dashboard, Settings    |

### User Flows

**Tutoring Flow:**
1. Student logs in → selects topic → types question
2. System routes to specialist agent → agent detects knowledge level and confusion
3. Agent selects strategy → generates response with tools if needed
4. Feedback check injected → a student continues or changes a topic

**Assessment Flow:**
1. Student navigates to Assessment page → chooses mode (exercise or LLM-generated)
2. System presents the question with rubric
3. Student submits answer → auto-grading with competency update
4. Score, feedback, and correct answer displayed
5. Spaced repetition review scheduled for tested concepts

**Exercise Progression Flow:**
1. Student views available exercises → Rank 1 unlocked by default
2. Student completes exercise with ≥50% score → next rank unlocked
3. Students can practice original or AI-generated similar variant
4. Locked exercises show prerequisite requirements

**Review Flow:**
1. System identifies concepts with `next_review_at ≤ now`
2. Due reviews surfaced in the agent conversation context
3. Students can start a formal review session → rate recall quality (0–5)
4. SM-2 recalculates interval and an ease factor → next review scheduled

---

## 9. Non-Functional Requirements

### Security

- JWT authentication with HS256 algorithm (32+ char secret)
- bcrypt password hashing with byte-length truncation
- Role-based access control (User/Admin)
- Domain-based registration approval (`@usach.cl` auto-activate)
- CORS middleware with configurable origins
- Log injection prevention (sanitization of user-controlled values)
- Auto-logout on 401 responses

### Rate Limiting

| Endpoint              | Limit            |
|-----------------------|------------------|
| Registration          | 5/minute per IP  |
| Login                 | 5/minute per IP  |
| Chat                  | 10/minute per IP |
| Assessment Generation | 5/minute per IP  |
| Assessment Submission | 10/minute per IP |
| Exercise Assessment   | 5/minute per IP  |

### Performance

- Database connection pooling: pool_size=5, max_overflow=10, pool_pre_ping=true
- Conversation history pagination (default 10 messages)
- Activity event batching (up to 50 per request)
- LLM tool-calling loop capped at three iterations
- 30-second HTTP client timeout

### Logging

- Dual-mode: standard (debug) and JSON (production)
- Log injection prevention via sanitization
- Structured logging with timestamps

### Database

- PostgreSQL via SQLAlchemy 2.0
- Schema created via `create_all` (no migrations)
- JSON columns for flexible metadata
- Indexes on: student_id, conversation_id, concept_id, timestamp

---

## 10. Configuration

All configuration via environment variables (`.env` file), managed by pydantic-settings.

| Variable                   | Default                      | Description                            |
|----------------------------|------------------------------|----------------------------------------|
| `LLM_PROVIDER`             | `gemini`                     | LLM provider (gemini/openai/anthropic) |
| `GEMINI_API_KEY`           | —                            | Google Gemini API key                  |
| `OPENAI_API_KEY`           | —                            | OpenAI API key                         |
| `ANTHROPIC_API_KEY`        | —                            | Anthropic API key                      |
| `GEMINI_MODEL`             | `gemini-2.5-flash-lite`      | Gemini model name                      |
| `OPENAI_MODEL`             | `gpt-4-turbo-preview`        | OpenAI model name                      |
| `ANTHROPIC_MODEL`          | `claude-3-5-sonnet-20241022` | Anthropic model name                   |
| `DATABASE_URL`             | —                            | PostgreSQL connection string           |
| `DATABASE_ECHO`            | `false`                      | SQL query logging                      |
| `SECRET_KEY`               | —                            | JWT signing secret (32+ chars)         |
| `ACCESS_TOKEN_EXPIRE_DAYS` | `7`                          | JWT token lifetime                     |
| `SESSION_TIMEOUT_MINUTES`  | `60`                         | Idle session timeout                   |
| `CORS_ORIGINS`             | `*`                          | Allowed CORS origins                   |
| `BACKEND_HOST`             | `0.0.0.0`                    | Backend bind address                   |
| `BACKEND_PORT`             | `8000`                       | Backend port                           |
| `FRONTEND_HOST`            | `localhost`                  | Frontend host                          |
| `FRONTEND_PORT`            | `8501`                       | Frontend port                          |
| `DEBUG`                    | `false`                      | Debug mode                             |
| `LOG_LEVEL`                | `INFO`                       | Logging level                          |
| `VERSION`                  | `1.6.4`                      | Application version                    |
