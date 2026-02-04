# Tools - Agent Capabilities

## Overview

The `tools/` directory contains LangChain-based tools that extend agent capabilities beyond pure text generation. Tools provide computational features, validation, visualization, and domain-specific functionality.

## Contents

| File/Directory    | Description                           |
|-------------------|---------------------------------------|
| `__init__.py`     | Package exports for all tools         |
| `modeling_tools/` | Tools for Mathematical Modeling Agent |
| `or_tools/`       | Tools for Operations Research Agent   |

## Architecture

```diagram
┌─────────────────────────────────────────────────────────────────┐
│                          Agent                                  │
│                  (e.g., MathematicalModelingAgent)              │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        LLM Service                              │
│                  generate_response_with_tools()                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
          ┌─────────────────────┴─────────────────────┐
          │                                           │
          ▼                                           ▼
┌─────────────────────┐                 ┌─────────────────────┐
│   modeling_tools/   │                 │     or_tools/       │
├─────────────────────┤                 ├─────────────────────┤
│ • ModelValidator    │                 │ • ProblemClassifier │
│ • ProblemSolver     │                 │ • TimelineExplorer  │
│ • RegionVisualizer  │                 └─────────────────────┘
│ • ExercisePractice  │
│ • ExerciseValidator │
└─────────────────────┘
```

## Tool Categories

### Modeling Tools

Tools for the Mathematical Modeling Agent to validate, solve, and visualize optimization problems:

| Tool                    | Purpose                            |
|-------------------------|------------------------------------|
| `ModelValidatorTool`    | Validate optimization formulations |
| `ProblemSolverTool`     | Solve optimization problems        |
| `RegionVisualizerTool`  | Visualize feasible regions         |
| `ExercisePracticeTool`  | Provide practice exercises         |
| `ExerciseValidatorTool` | Validate student formulations      |

### OR Tools

Tools for the Operations Research Agent to classify and contextualize problems:

| Tool                    | Purpose                                     |
|-------------------------|---------------------------------------------|
| `ProblemClassifierTool` | Classify problem types and recommend agents |
| `TimelineExplorerTool`  | Provide historical context                  |

## Business Logic

### Tool Binding

Tools are bound to the LLM during response generation:

```python
# In agent or LLM service
from app.tools.modeling_tools import ModelValidatorTool, ProblemSolverTool

tools = [ModelValidatorTool(), ProblemSolverTool()]
llm_with_tools = llm.bind_tools(tools)
```

### Tool Execution Flow

1. **LLM receives message** with available tools
2. **LLM decides** to call one or more tools
3. **Service executes** tool via `_run()` method
4. **Result returned** to LLM as ToolMessage
5. **LLM incorporates** result into response
6. **Loop continues** until no more tool calls (max three iterations)

### Tool Interface

All tools extend `langchain_core.tools.BaseTool`:

```python
from langchain_core.tools import BaseTool

class MyTool(BaseTool):
    name: str = "my_tool"
    description: str = """Tool description for LLM..."""

    def _run(self, input: str) -> str:
        # Tool logic here
        return "result"
```

## Exported Tools

From `__init__.py`:

```python
from .modeling_tools import (
    ModelValidatorTool,
    ProblemSolverTool,
    RegionVisualizerTool,
)
from .or_tools import ProblemClassifierTool, TimelineExplorerTool

__all__ = [
    # OR Tools
    "TimelineExplorerTool",
    "ProblemClassifierTool",
    # Modeling Tools
    "ModelValidatorTool",
    "ProblemSolverTool",
    "RegionVisualizerTool",
]
```

## Usage

### Using Tools in an Agent

```python
from app.tools import ModelValidatorTool, ProblemSolverTool
from app.services.llm_service import get_llm_service

llm_service = get_llm_service()

tools = [ModelValidatorTool(), ProblemSolverTool()]

response = llm_service.generate_response_with_tools(
    messages=[{"role": "user", "content": "Validate this model..."}],
    tools=tools,
    system_prompt="You are a mathematical modeling tutor..."
)
```

### Creating a New Tool

1. Create a tool class in the appropriate subdirectory:

```python
# tools/modeling_tools/my_new_tool.py
from langchain_core.tools import BaseTool
import logging

logger = logging.getLogger(__name__)

class MyNewTool(BaseTool):
    name: str = "my_new_tool"
    description: str = """Description of what this tool does.

    Input: What the tool expects
    Output: What it returns

    Use this when [conditions]."""

    model_config = {"arbitrary_types_allowed": True}

    def _run(self, input_param: str) -> str:
        try:
            # Tool logic
            result = self._process(input_param)
            logger.info(f"Tool executed successfully")
            return result
        except Exception as e:
            logger.error(f"Tool error: {e}")
            return f"Error: {str(e)}"

    def _process(self, param: str) -> str:
        # Implementation
        return "processed result"
```

2. Export from `__init__.py`:

```python
# tools/modeling_tools/__init__.py
from .my_new_tool import MyNewTool

__all__ = [
    # ... existing tools
    "MyNewTool",
]
```

3. Use in agent:

```python
from app.tools.modeling_tools import MyNewTool

tools = [MyNewTool()]
```

## Changelog

- **v1.0.0** (2026-01-05): Initial documentation
- **v1.1.0** (2026-02-03): Added some tools, exercise features, basic user restrictiveness to `@usach` domain
