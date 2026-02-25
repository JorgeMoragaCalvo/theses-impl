# Agents - AI Tutoring Agents

## Overview

The `agents/` directory contains specialized AI tutoring agents for different optimization topics. Each agent inherits from `BaseAgent` and provides topic-specific tutoring with adaptive learning capabilities.

## Contents

| File                             | Description                                       |
|----------------------------------|---------------------------------------------------|
| `base_agent.py`                  | Abstract base class with core agent functionality |
| `linear_programming_agent.py`    | Agent for Linear Programming (LP)                 |
| `integer_programming_agent.py`   | Agent for Integer Programming (IP)                |
| `nonlinear_programming_agent.py` | Agent for Nonlinear Programming (NLP)             |
| `nlp_agent.py`                   | Alternative NLP agent implementation              |
| `mathematical_modeling_agent.py` | Agent for Mathematical Modeling (with tools)      |
| `operations_research_agent.py`   | Agent for general Operations Research             |
| `__init__.py`                    | Package initialization                            |

## Architecture

```diagram
                    ┌──────────────────────────────┐
                    │          BaseAgent            │
                    │          (Abstract)           │
                    ├──────────────────────────────┤
                    │ - agent_name                 │
                    │ - agent_type                 │
                    │ - llm_service                │
                    │ - course_materials           │
                    ├──────────────────────────────┤
                    │ + get_system_prompt()        │
                    │ + get_available_strategies() │
                    │ + generate_response()        │
                    │ + a_generate_response()      │
                    │ + detect_confusion()         │
                    │ + select_strategy()          │
                    │ + validate_message()         │
                    │ + format_review_context()    │
                    │ + build_enhanced_prompt()    │
                    │ + get_agent_info()           │
                    └──────────────┬───────────────┘
                                   │
          ┌──────────┬─────────────┼─────────────┬──────────┐
          │          │             │             │          │
          ▼          ▼             ▼             ▼          ▼
     ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
     │   LP    │ │   IP    │ │   NLP   │ │   MM    │ │   OR    │
     │  Agent  │ │  Agent  │ │  Agent  │ │  Agent  │ │  Agent  │
     └─────────┘ └─────────┘ └─────────┘ └────┬────┘ └─────────┘
                                               │
                                               ▼
                                ┌───────────────────────────┐
                                │      Modeling Tools       │
                                ├───────────────────────────┤
                                │ ModelValidatorTool        │
                                │ ProblemSolverTool         │
                                │ RegionVisualizerTool      │
                                │ ExercisePracticeTool      │
                                │ ExerciseValidatorTool     │
                                └───────────────────────────┘
```

## BaseAgent Features

### Core Methods

| Method                                         | Description                                       |
|------------------------------------------------|---------------------------------------------------|
| `get_system_prompt(context)`                   | Abstract - generates topic-specific system prompt |
| `get_available_strategies()`                   | Abstract - returns list of explanation strategies |
| `generate_response(message, history, context)` | Generates AI response using LLM                   |
| `a_generate_response(...)`                     | Async version of generate_response                |
| `load_course_materials(path)`                  | Loads course materials from file                  |
| `format_context_for_prompt(context)`           | Formats student context for prompts               |
| `get_agent_info()`                             | Returns agent information dictionary              |

### Message Processing Methods

| Method                           | Description                         |
|----------------------------------|-------------------------------------|
| `validate_message(message)`      | Validates message format and length |
| `preprocess_message(message)`    | Cleans and normalizes user message  |
| `postprocess_response(response)` | Cleans response before returning    |

### Adaptive Learning Methods

| Method                                                        | Description                         |
|---------------------------------------------------------------|-------------------------------------|
| `detect_student_confusion(message, history)`                  | Analyzes for confusion signals      |
| `select_explanation_strategy(confusion, knowledge, previous)` | Chooses best strategy               |
| `build_adaptive_prompt_section(analysis, strategy, context)`  | Creates adaptive instructions       |
| `should_add_feedback_request(...)`                            | Determines if feedback check needed |
| `add_feedback_request_to_response(...)`                       | Appends understanding check-in      |

### Spaced Repetition Methods

| Method                                                  | Description                                           |
|---------------------------------------------------------|-------------------------------------------------------|
| `build_enhanced_system_prompt(base, adaptive, context)` | Combines base, adaptive, and review prompts           |
| `format_review_context(due_reviews)`                    | Formats spaced repetition reviews into prompt section |

### Internal Helper Methods

These shared methods reduce code duplication across agent subclasses:

| Method                                                        | Description                                     |
|---------------------------------------------------------------|-------------------------------------------------|
| `_validate_and_preprocess(message)`                           | Validates and preprocesses user message         |
| `_prepare_generation_components(message, history, context)`   | Prepares all components for response generation |
| `_generate_and_postprocess(components, history, context)`     | Generates response and postprocesses (sync)     |
| `_a_generate_and_postprocess(components, history, context)`   | Generates response and postprocesses (async)    |
| `_postprocess_with_feedback(response, history, context, ...)` | Shared postprocessing with feedback logic       |

### Confusion Detection

The system detects confusion through:
- Keyword analysis ("confused", "don't understand", "lost", etc.)
- Repeated topic detection
- Question pattern analysis

Confusion levels: `none`, `low`, `medium`, `high`

### Explanation Strategies

| Strategy              | Description                      | Best For                  |
|-----------------------|----------------------------------|---------------------------|
| `step-by-step`        | Numbered sequential steps        | High confusion, beginners |
| `example-based`       | Concrete numerical examples      | Medium confusion          |
| `conceptual`          | Focus on underlying ideas        | Intermediate+ students    |
| `analogy-based`       | Relate to familiar concepts      | High confusion            |
| `visual`              | Geometric/graphical descriptions | Spatial concepts          |
| `formal-mathematical` | Rigorous definitions             | Advanced students         |
| `comparative`         | Compare with related concepts    | Intermediate+ students    |

## Agent Registry

Agents are registered in `main.py`:

```python
AGENT_REGISTRY = {
    "operations_research": get_operations_research_agent,
    "linear_programming": get_linear_programming_agent,
    "mathematical_modeling": get_mathematical_modeling_agent,
    "nonlinear_programming": get_nonlinear_programming_agent,
    "integer_programming": get_integer_programming_agent
}
```

## Business Logic

### Response Generation Flow

1. **Validation & Preprocessing** (`_validate_and_preprocess`)
   - Validate message format and length
   - Clean and normalize user input

2. **Component Preparation** (`_prepare_generation_components`)
   - Get student knowledge level
   - Format conversation history
   - Load course materials if available
   - Detect confusion signals and determine confusion level
   - Select an explanation strategy based on knowledge and confusion level
   - Build an adaptive prompt section (if confusion is detected)
   - Build enhanced system prompt with spaced repetition reviews

3. **Response Generation** (`_generate_and_postprocess` / `_a_generate_and_postprocess`)
   - Send to LLM via LLMService
   - Optional: Execute tools (MathematicalModelingAgent)
   - Post-process response

4. **Feedback & Postprocessing** (`_postprocess_with_feedback`)
   - Clean and normalize LLM output
   - Optionally append understanding check-in

### Mathematical Modeling Agent (Special)

The Mathematical Modeling Agent has additional capabilities:
- Uses LangChain tools for validation and solving
- Generates responses with tool calling support
- Available tools:
  - `ModelValidatorTool` - Validates optimization model formulations
  - `ProblemSolverTool` - Solves optimization problems
  - `RegionVisualizerTool` - Visualizes 2D feasible regions
  - `ExercisePracticeTool` - Provides practice exercises
  - `ExerciseValidatorTool` - Validates student formulations

## Usage

### Getting an Agent

```python
from app.agents.linear_programming_agent import get_linear_programming_agent

agent = get_linear_programming_agent()
response = agent.generate_response(
    user_message="Explain the simplex method",
    conversation_history=[],
    context={"student": {"knowledge_level": "beginner"}}
)
```

### Creating a New Agent

1. Create a new file in `agents/`:

```python
from .base_agent import BaseAgent

class MyNewAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="My New Agent",
            agent_type="my_new_topic"
        )
        # Load course materials if available
        self.load_course_materials("path/to/materials.md")

    def get_system_prompt(self, context: dict) -> str:
        # Build topic-specific prompt
        return """You are an expert tutor in [topic]..."""

# Factory function
_agent_instance = None

def get_my_new_agent():
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = MyNewAgent()
    return _agent_instance
```

2. Register in `main.py`:

```python
from .agents.my_new_agent import get_my_new_agent

AGENT_REGISTRY["my_new_topic"] = get_my_new_agent
```

3. Add a topic to `database.py` Topic enum:

```python
class Topic(str, enum.Enum):
    # ... existing topics
    MY_NEW_TOPIC = "my_new_topic"
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