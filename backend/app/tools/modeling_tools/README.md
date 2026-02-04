# Modeling Tools - Mathematical Modeling Agent Tools

## Overview

The `modeling_tools/` directory contains LangChain tools that enhance the Mathematical Modeling Agent's tutoring capabilities with computational and validation features.

## Contents

| File                    | Description                                       |
|-------------------------|---------------------------------------------------|
| `model_validator.py`    | Validates optimization model formulations         |
| `problem_solver.py`     | Solves optimization problems                      |
| `region_visualizer.py`  | Visualizes feasible regions                       |
| `exercise_practice.py`  | Provides practice exercises                       |
| `exercise_validator.py` | Validates student formulations against references |
| `__init__.py`           | Package exports                                   |

## Tools

### ModelValidatorTool

**Purpose**: Validates optimization model formulations for syntactic correctness and logical consistency.

**Checks**:
- Variable definitions (names, types, bounds)
- Objective function syntax and variable references
- Constraint syntax and variable references
- Logical consistency

**Input Schema**:
```json
{
  "variables": [
    {"name": "x1", "type": "continuous", "lower": 0},
    {"name": "x2", "type": "integer", "lower": 0, "upper": 10}
  ],
  "objective": {
    "sense": "maximize",
    "expression": "3*x1 + 5*x2"
  },
  "constraints": [
    {"expression": "x1 + 2*x2 <= 10", "name": "resource1"},
    {"expression": "2*x1 + x2 >= 4", "name": "demand"}
  ]
}
```

**Valid Variable Types**: `continuous`, `integer`, `binary` (also accepts Spanish: `continua`, `entera`, `binaria`)

**Valid Objective Senses**: `maximize`, `minimize`, `max`, `min` (also: `maximizar`, `minimizar`)

**Output**: Validation result with errors, warnings, and summary.

---

### ProblemSolverTool

**Purpose**: Solves optimization problems and returns optimal solutions.

**Supported Problem Types**:
- Linear Programming (LP)
- Integer Programming (IP)
- Mixed Integer Programming (MIP)

**Input**: JSON model specification (same as ModelValidatorTool)

**Output**: Solution with optimal values, objective value, and status.

---

### RegionVisualizerTool

**Purpose**: Creates visualizations of feasible regions for 2D linear programming problems.

**Features**:
- Plots constraint lines
- Shades-feasible region
- Marks corner points
- Shows optimal solution

**Input**: JSON with 2D constraints

**Output**: Description of visualization or base64-encoded image.

---

### ExercisePracticeTool

**Purpose**: Provides practice exercises from the exercise bank.

**Features**:
- Lists available exercises
- Retrieves exercise details
- Supports different difficulty levels

**Input**: Exercise request parameters

**Output**: Exercise statement and metadata.

---

### ExerciseValidatorTool

**Purpose**: Validates student formulations against reference solutions.

**Features**:
- Compares variable definitions
- Checks objective function equivalence
- Validates constraint coverage
- Provides detailed feedback

**Input**:
```json
{
  "student_model": {...},
  "exercise_id": "MM-01_steel"
}
```

**Output**: Validation results with score and feedback.

## Business Logic

### Validation Rules

#### Variables
- Names must be alphanumeric (start with a letter)
- Types must be valid (continuous/integer/binary)
- Lower bounds cannot exceed upper bounds
- Binary variables have implicit bounds [0, 1]

#### Objective
- Sense must be maximized or minimize
- Expression must reference defined variables
- Syntax must be valid mathematical expression

#### Constraints
- Expression must include comparison operator (<=, >=, =, <, >)
- All referenced variables must be defined
- Names are optional but recommended

### Error Severity

| Level   | Description                     |
|---------|---------------------------------|
| Error   | Invalid model, cannot proceed   |
| Warning | Potential issue, model may work |
| Info    | Suggestion for improvement      |

## Usage

### Using ModelValidatorTool

```python
from app.tools.modeling_tools import ModelValidatorTool

validator = ModelValidatorTool()

model_json = '''
{
  "variables": [
    {"name": "x1", "type": "continuous", "lower": 0},
    {"name": "x2", "type": "continuous", "lower": 0}
  ],
  "objective": {
    "sense": "maximize",
    "expression": "3*x1 + 2*x2"
  },
  "constraints": [
    {"expression": "x1 + x2 <= 4", "name": "resource"}
  ]
}
'''

result = validator._run(model_json)
print(result)
```

### Using with LLM

```python
from app.tools.modeling_tools import ModelValidatorTool, ProblemSolverTool
from app.services.llm_service import get_llm_service

llm_service = get_llm_service()

tools = [ModelValidatorTool(), ProblemSolverTool()]

response = llm_service.generate_response_with_tools(
    messages=[{
        "role": "user",
        "content": "Validate and solve: max 3x+2y subject to x+y<=4, x,y>=0"
    }],
    tools=tools,
    system_prompt="You are a mathematical modeling tutor. Use tools to validate and solve problems."
)
```

## Exported

From `__init__.py`:

```python
from .model_validator import ModelValidatorTool
from .problem_solver import ProblemSolverTool
from .region_visualizer import RegionVisualizerTool
from .exercise_practice import ExercisePracticeTool
from .exercise_validator import ExerciseValidatorTool

__all__ = [
    "ModelValidatorTool",
    "ProblemSolverTool",
    "RegionVisualizerTool",
    "ExercisePracticeTool",
    "ExerciseValidatorTool",
]
```

## Changelog

- **v1.0.0** (2026-01-05): Initial documentation
- **v1.1.0** (2026-02-03): Added some tools, exercise features, basic user restrictiveness to `@usach` domain
