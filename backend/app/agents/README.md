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
                    ┌─────────────────────┐
                    │     BaseAgent       │
                    │     (Abstract)      │
                    ├─────────────────────┤
                    │ - agent_name        │
                    │ - agent_type        │
                    │ - llm_service       │
                    │ - course_materials  │
                    ├─────────────────────┤
                    │ + get_system_prompt │
                    │ + generate_response │
                    │ + detect_confusion  │
                    │ + select_strategy   │
                    └──────────┬──────────┘
                               │
        ┌──────────┬───────────┼───────────┬──────────┐
        │          │           │           │          │
        ▼          ▼           ▼           ▼          ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
   │   LP    │ │   IP    │ │   NLP   │ │   MM    │ │   OR    │
   │  Agent  │ │  Agent  │ │  Agent  │ │  Agent  │ │  Agent  │
   └─────────┘ └─────────┘ └─────────┘ └────┬────┘ └─────────┘
                                            │
                                            ▼
                                    ┌───────────────┐
                                    │ Modeling      │
                                    │ Tools         │
                                    └───────────────┘
```

## BaseAgent Features

### Core Methods

| Method                                         | Description                                       |
|------------------------------------------------|---------------------------------------------------|
| `get_system_prompt(context)`                   | Abstract - generates topic-specific system prompt |
| `generate_response(message, history, context)` | Generates AI response using LLM                   |
| `a_generate_response(...)`                     | Async version of generate_response                |
| `load_course_materials(path)`                  | Loads course materials from file                  |
| `format_context_for_prompt(context)`           | Formats student context for prompts               |

### Adaptive Learning Methods

| Method                                                        | Description                         |
|---------------------------------------------------------------|-------------------------------------|
| `detect_student_confusion(message, history)`                  | Analyzes for confusion signals      |
| `select_explanation_strategy(confusion, knowledge, previous)` | Chooses best strategy               |
| `build_adaptive_prompt_section(analysis, strategy, context)`  | Creates adaptive instructions       |
| `should_add_feedback_request(...)`                            | Determines if feedback check needed |
| `add_feedback_request_to_response(...)`                       | Appends understanding check-in      |

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

1. **Context Preparation**
   - Get student knowledge level
   - Format conversation history
   - Load course materials if available

2. **Confusion Analysis**
   - Detect confusion signals in a message
   - Check for repeated topics
   - Determine confusion level

3. **Strategy Selection**
   - Consider knowledge level
   - Consider the confusion level
   - Avoid recently used strategies

4. **Prompt Construction**
   - Base system prompt (topic-specific)
   - Context section (student info)
   - Adaptive instructions (if confusion is detected)
   - Course materials reference

5. **Response Generation**
   - Send to LLM via LLMService
   - Optional: Execute tools (MathematicalModelingAgent)
   - Post-process response

6. **Feedback Check**
   - Optionally append understanding check-in

### Mathematical Modeling Agent (Special)

The Mathematical Modeling Agent has additional capabilities:
- Uses LangChain tools for validation and solving
- Can execute `ModelValidatorTool`, `ProblemSolverTool`, etc.
- Generates responses with tool calling support

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