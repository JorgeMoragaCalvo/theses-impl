# OR Tools – Operations Research Agent Tools

## Overview

The `or_tools/` directory contains LangChain tools that support the Operations Research Agent's educational mission by providing problem classification and historical context.

## Contents

| File                    | Description                                            |
|-------------------------|--------------------------------------------------------|
| `problem_classifier.py` | Classifies optimization problems and recommends agents |
| `timeline_explorer.py`  | Provides historical context and timeline information   |
| `__init__.py`           | Package exports                                        |

## Tools

### ProblemClassifierTool

**Purpose**: Analyzes problem descriptions to identify the type of optimization problem and recommend the appropriate specialized agent.

**Analyzes**:
- Variable types (continuous, integer, binary)
- Relationship types (linear, nonlinear)
- Problem structure
- Special characteristics (network, stochastic, etc.)

**Classifications**:

| Type       | Description               | Recommended Agent         |
|------------|---------------------------|---------------------------|
| LP         | Linear Programming        | LinearProgrammingAgent    |
| IP         | Integer Programming       | IntegerProgrammingAgent   |
| MIP        | Mixed Integer Programming | IntegerProgrammingAgent   |
| NLP        | Nonlinear Programming     | NonlinearProgrammingAgent |
| Network    | Network flow problems     | OperationsResearchAgent   |
| Stochastic | Problems with uncertainty | OperationsResearchAgent   |

**Input**: Natural language problem description

**Output**:
```
Problem Classification Results:

Classification: Mixed Integer Programming (MIP)

Key Characteristics Detected:
- Has integer variables: Yes (detected keywords: "units", "select")
- Has continuous variables: Yes
- Linear relationships: Yes
- Network structure: No

Recommended Agent: IntegerProgrammingAgent

Explanation: This problem involves both continuous and integer decision
variables with linear constraints, making it a Mixed Integer Program...
```

**Detection Keywords**:
- Integer vars: "integer", "whole", "units", "select", "assign"
- Binary vars: "yes/no", "binary", "select", "choose", "0 or 1"
- Nonlinear: "quadratic", "exponential", "logarithm", "product of variables"
- Network: "flow", "path", "route", "transportation", "assignment"
- Uncertainty: "random", "probability", "uncertain", "stochastic"

---

### TimelineExplorerTool

**Purpose**: Provides historical context about optimization methods and their development.

**Topics Covered**:
- History of Linear Programming (Dantzig, Simplex, etc.)
- Development of Integer Programming
- Evolution of Nonlinear Programming
- Key figures in Operations Research
- Important algorithms and their origins

**Input**: Query about historical context

**Output**: Historical narrative with relevant dates and figures.

## Business Logic

### Problem Classification Algorithm

1. **Keyword Extraction**: Scan for domain-specific terms
2. **Characteristic Detection**:
   - Check for integer/binary variable indicators
   - Check for nonlinearity indicators
   - Check for special structures
3. **Classification Mapping**:
   - Binary only → IP
   - Integer + Continuous → MIP
   - Nonlinear terms → NLP
   - Otherwise → LP
4. **Agent Recommendation**: Map classification to agent

### Classification Priority

When multiple characteristics are detected:
1. Nonlinearity takes precedence
2. Then integer variables
3. Special structures (network, stochastic) as modifiers
4. Default to LP if no special characteristics

## Usage

### Using ProblemClassifierTool

```python
from app.tools.or_tools import ProblemClassifierTool

classifier = ProblemClassifierTool()

problem = """
A company needs to decide how many units of products A and B to produce.
Each unit of A requires 2 hours of labor and 3 units of material.
Each unit of B requires 1 hour of labor and 4 units of material.
Available: 100 hours of labor, 200 units of material.
Profit: $5 per unit of A, $4 per unit of B.
Maximize profit.
"""

result = classifier._run(problem)
print(result)
```

### Using with LLM

```python
from app.tools.or_tools import ProblemClassifierTool, TimelineExplorerTool
from app.services.llm_service import get_llm_service

llm_service = get_llm_service()

tools = [ProblemClassifierTool(), TimelineExplorerTool()]

response = llm_service.generate_response_with_tools(
    messages=[{
        "role": "user",
        "content": "I have a scheduling problem where I need to assign workers to shifts. What type of problem is this?"
    }],
    tools=tools,
    system_prompt="You are an Operations Research tutor. Help students classify and understand optimization problems."
)
```

## Exported

From `__init__.py`:

```python
from .problem_classifier import ProblemClassifierTool
from .timeline_explorer import TimelineExplorerTool

__all__ = [
    "TimelineExplorerTool",
    "ProblemClassifierTool",
]
```

## Changelog

- **v1.0.0** (2026-01-05): Initial documentation
- **v1.1.0** (2026-02-03): Added some tools, exercise features, basic user restrictiveness to `@usach` domain
