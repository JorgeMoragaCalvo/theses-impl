# Services – Business Logic Layer

## Overview

The `services/` directory contains the business logic layer of the application. Services encapsulate complex operations, interact with the database, and coordinate between different components.

## Contents

| File                             | Description                                                |
|----------------------------------|------------------------------------------------------------|
| `llm_service.py`                 | Multi-provider LLM abstraction (OpenAI, Anthropic, Google) |
| `conversation_service.py`        | Conversation history, context, and progress tracking       |
| `assessment_service.py`          | Personalized assessment generation                         |
| `grading_service.py`             | Automatic assessment grading using LLM                     |
| `exercise_manager.py`            | Exercise loading and management                            |
| `exercise_assessment_service.py` | Exercise-based assessment creation                         |
| `exercise_progress_service.py`   | Exercise completion tracking and progression gating        |
| `competency_service.py`          | Concept-level mastery tracking using EWA                   |
| `analytics_service.py`           | Student activity recording and admin dashboard metrics     |
| `spaced_repetition_service.py`   | SM-2 spaced repetition scheduling for concept reviews      |
| `llm_response_parser.py`         | JSON extraction from LLM responses                         |
| `__init__.py`                    | Package initialization                                     |

## Service Architecture

```diagram
┌─────────────────────────────────────────────────────────────────┐
│                         Endpoints                               │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Service Layer                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Conversation   │  │   Assessment    │  │    Grading      │  │
│  │    Service      │  │    Service      │  │    Service      │  │
│  │                 │  │                 │  │                 │  │
│  │ - get_history   │  │ - generate      │  │ - grade         │  │
│  │ - get_context   │  │ - personalize   │  │ - score         │  │
│  │ - progress      │  │                 │  │ - feedback      │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
│           │                    │                    │           │
│           └────────────────────┼────────────────────┘           │
│                                ▼                                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                       LLM Service                           ││
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                      ││
│  │  │ OpenAI  │  │Anthropic│  │ Google  │                      ││
│  │  └─────────┘  └─────────┘  └─────────┘                      ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Exercise        │  │ Exercise        │  │ Exercise        │  │
│  │ Manager         │  │ Assessment Svc  │  │ Progress Svc    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Competency      │  │ Spaced          │  │ Analytics       │  │
│  │ Service         │  │ Repetition Svc  │  │ Service         │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Database                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Service Details

### LLMService (`llm_service.py`)

**Purpose**: Unified interface for multiple LLM providers.

**Supported Providers**:
- Google Gemini (`gemini`, `google`)
- OpenAI (`openai`)
- Anthropic (`anthropic`)

**Key Methods**:

| Method                                          | Description                  |
|-------------------------------------------------|------------------------------|
| `generate_response(messages, system_prompt)`    | Generate text response       |
| `a_generate_response(...)`                      | Async version                |
| `generate_response_with_tools(messages, tools)` | Response with tool calling   |
| `a_generate_response_with_tools(...)`           | Async version with tools     |
| `get_provider_info()`                           | Get current provider details |

**Tool Calling Flow**:
1. LLM receives messages and tool definitions
2. LLM decides to call tool(s)
3. Service executes tool(s) via `_execute_tool()`
4. Tool results added to conversation
5. LLM generates final response
6. Max 3 iterations (configurable)

### ConversationService (`conversation_service.py`)

**Purpose**: Manage conversation state and student context.

**Key Methods**:

| Method                                                 | Description                         |
|--------------------------------------------------------|-------------------------------------|
| `get_conversation_history(id, limit)`                  | Get recent messages                 |
| `get_student_context(student_id, topic)`               | Get student personalization context |
| `get_conversation_context(conv_id, student_id, topic)` | Combined context                    |
| `compute_student_progress(student_id)`                 | Calculate progress metrics          |

**Context Structure**:
```python
{
    "student_id": 1,
    "student_name": "John",
    "knowledge_level": "intermediate",
    "knowledge_level_description": "...",
    "preferences": {},
    "all_knowledge_levels": {...},
    "assessment_performance": {...}  # if include_assessment_data=True
}
```

### AssessmentService (`assessment_service.py`)

**Purpose**: Generate personalized assessments using LLM.

**Key Methods**:

| Method                                                            | Description           |
|-------------------------------------------------------------------|-----------------------|
| `generate_personalized_assessment(student_id, topic, difficulty)` | Create new assessment |

**Assessment Generation**:
1. Analyze student's knowledge gaps
2. Review recent conversation topics
3. Generate question via LLM
4. Include correct answer and rubric
5. Return structured assessment data

### GradingService (`grading_service.py`)

**Purpose**: Automatically grade student answers.

**Key Methods**:

| Method                         | Description                       |
|--------------------------------|-----------------------------------|
| `grade_assessment(assessment)` | Grade and return score + feedback |

**Grading Process**:
1. Compare student answer against correct answer
2. Apply rubric criteria
3. LLM generates score (0-max_score) and feedback
4. Parse JSON response for score/feedback

### ExerciseManager (`exercise_manager.py`)

**Purpose**: Load and manage pre-built exercises.

**Key Methods**:

| Method                      | Description                 |
|-----------------------------|-----------------------------|
| `list_exercises()`          | Get all available exercises |
| `get_exercise(exercise_id)` | Get specific exercise       |

**Exercise Structure**:
```python
{
    "id": "MM-01_steel",
    "title": "Steel Production Problem",
    "difficulty": "intermediate",
    "statement": "...",
    "reference_solution": {...},
    "rubric": "..."
}
```

### ExerciseAssessmentService (`exercise_assessment_service.py`)

**Purpose**: Create assessments from pre-built exercises.

**Modes**:
- `practice`: Use exercise directly as assessment
- `similar`: Generate similar problem via LLM

**Key Methods**:

| Method                                 | Description                     |
|----------------------------------------|---------------------------------|
| `create_assessment(exercise_id, mode)` | Create assessment from exercise |
| `get_exercise_preview(exercise_id)`    | Get exercise without solution   |

### LLMResponseParser (`llm_response_parser.py`)

**Purpose**: Extract JSON from LLM responses.

**Key Methods**:

| Method                   | Description                   |
|--------------------------|-------------------------------|
| `extract_json(response)` | Parse JSON from response text |

**Handles**:
- Markdown code blocks
- Nested JSON
- Fallback parsing

### ExerciseProgressService (`exercise_progress_service.py`)

**Purpose**: Track student exercise completion and enforce per-topic progression gating.

**Key Functions**:

| Function                                          | Description                                       |
|---------------------------------------------------|---------------------------------------------------|
| `get_completed_exercise_ids(db, student_id, topic)` | Get exercise IDs the student has completed (>=50% score) |
| `compute_max_unlocked_rank(completed_ids, exercises)` | Compute the highest unlocked rank for a topic     |
| `get_exercises_with_progress(db, student_id, topic)` | Return exercises enriched with `locked` and `completed` fields |

**Progression Rules**:
- Rank 1 exercises are always unlocked
- Rank 0 (unranked) exercises are always unlocked
- Completing any exercise at rank N unlocks rank N+1
- "Completing" means achieving >= 50% of max_score

### CompetencyService (`competency_service.py`)

**Purpose**: Track student mastery of individual concepts using Exponentially Weighted Average (EWA).

**Key Methods**:

| Method                                              | Description                                     |
|-----------------------------------------------------|-------------------------------------------------|
| `seed_concept_hierarchy()`                          | Populate ConceptHierarchy from taxonomy JSON files |
| `update_competency(student_id, concept_id, is_correct, score)` | Update mastery record using EWA              |
| `get_student_competencies(student_id, topic)`       | Get all competency records for a student/topic  |
| `get_mastery_summary(student_id, topic)`            | Summarize mastery levels across all concepts    |
| `get_next_concepts_to_learn(student_id, topic)`     | Recommend concepts based on prerequisite mastery |

**Mastery Levels** (thresholds):
- `MASTERED`: score >= 0.85, min 5 attempts
- `PROFICIENT`: score >= 0.60, min 3 attempts
- `DEVELOPING`: score >= 0.30
- `NOVICE`: score < 0.30
- `NOT_STARTED`: 0 attempts

**EWA Parameters**:
- Learning rate (alpha): 0.3
- Formula: `new_score = alpha * performance + (1 - alpha) * old_score`

**Includes**: `ConceptTaxonomyRegistry` singleton that loads and caches concept taxonomy JSON files from `data/concept_taxonomies/`.

### AnalyticsService (`analytics_service.py`)

**Purpose**: Record student activity events and provide aggregated metrics for the admin dashboard.

**Key Methods**:

| Method                                         | Description                              |
|------------------------------------------------|------------------------------------------|
| `record_events(student_id, events)`            | Batch insert activity events             |
| `get_daily_active_users(start, end)`           | Count distinct students per day          |
| `get_avg_session_duration(start, end)`         | Average session duration per day         |
| `get_peak_usage_hours(start, end)`             | Event counts per hour of day             |
| `get_page_popularity(start, end)`              | Visit counts and avg duration per page   |
| `get_topic_popularity(start, end)`             | Interaction counts per topic             |
| `get_user_engagement(start, end)`              | Aggregated engagement metrics            |
| `get_analytics_summary(days=30)`               | Combined summary for the last N days     |

### SpacedRepetitionService (`spaced_repetition_service.py`)

**Purpose**: SM-2 algorithm implementation for scheduling concept reviews at increasing intervals based on recall quality.

**Key Methods**:

| Method                                                     | Description                                    |
|------------------------------------------------------------|------------------------------------------------|
| `calculate_next_review(competency, quality)`               | SM-2: compute next review date and ease factor |
| `get_due_reviews(student_id, topic, limit)`                | Get competencies due for review                |
| `create_review_session(student_id, concept_id)`            | Start a new review session                     |
| `complete_review(session_id, quality, response_time)`      | Record result and schedule next review         |
| `schedule_initial_review(student_id, concept_id)`          | Schedule first review after initial study      |

**SM-2 Quality Scale** (0-5):
- 0: Complete blackout
- 1: Incorrect; correct answer remembered on seeing it
- 2: Incorrect; correct answer seemed easy to recall
- 3: Correct with serious difficulty
- 4: Correct after hesitation
- 5: Perfect response

**SM-2 Parameters**:
- Initial intervals: 1, 3, 7, 14, 30, 60 days
- Minimum ease factor: 1.3
- Default ease factor: 2.5
- Passing threshold: quality >= 3

## Business Logic

### Service Instantiation

Services use factory functions for singleton-like behavior:

```python
# Global instance
_llm_service: LLMService | None = None

def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
```

### Dependency Injection

Services requiring database access use FastAPI dependencies:

```python
def get_conversation_service(db: Session = Depends(get_db)):
    return ConversationService(db)
```

### Error Handling

Services implement graceful error handling:
- Log errors with context
- Return sensible defaults when possible
- Raise exceptions for critical failures

## Usage

### Getting a Service

```python
from app.services.llm_service import get_llm_service
from app.services.conversation_service import get_conversation_service

# Global singleton
llm = get_llm_service()

# With database session (in endpoint)
@app.get("/example")
async def example(db: Session = Depends(get_db)):
    conv_service = get_conversation_service(db)
    history = conv_service.get_conversation_history(conversation_id=1)
```

### Creating a New Service

```python
# services/my_service.py
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class MyService:
    def __init__(self, db: Session):
        self.db = db

    def my_method(self, param: str) -> dict:
        try:
            # Business logic here
            return {"result": "success"}
        except Exception as e:
            logger.error(f"Error in my_method: {e}")
            raise

def get_my_service(db: Session):
    return MyService(db)
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