# Unit Tests

Isolated unit tests that verify individual services and utilities without hitting the database or external APIs. All dependencies are mocked.

## Modules covered

### Agents & tutoring logic
- **Agent routing** (`test_agent_routing.py`) — LLM agent selection logic.
- **Agent topic check** (`test_agent_topic_check.py`) — topic-scope validation per agent.
- **Base agent** (`test_base_agent.py`) — shared base-agent behavior.
- **Strategy selection** (`test_strategy_selection.py`) — explanation-strategy selection logic.

### Core services
- **Auth** (`test_auth.py`) — password hashing and JWT token utilities.
- **Competency service** (`test_competency_service.py`) — concept mastery tracking and updates.
- **Conversation service** (`test_conversation_service.py`) — chat conversation management.
- **Grading service** (`test_grading_service.py`) — answer evaluation logic.
- **LLM response parser** (`test_llm_response_parser.py`) — structured output parsing from LLM responses.

### Knowledge tracing & scheduling
- **BKT service** (`test_bkt_service.py`) — Bayesian Knowledge Tracing posterior.
- **Spaced repetition** (`test_spaced_repetition.py`) — SM-2 algorithm for review scheduling.
- **Spaced repetition tool** (`test_spaced_repetition_tool.py`) — review-session tool used by agents.

### Exercises
- **Exercise progress service** (`test_exercise_progress_service.py`) — attempt tracking, scoring, and gating.
- **Exercise practice** (`test_exercise_practice.py`) — practice-exercise tool.
- **Exercise validator** (`test_exercise_validator.py`) — student-formulation validation.

### Solver & modeling tools
- **Branch and bound** (`test_branch_and_bound.py`) — branch-and-bound solver tool.
- **Simplex solver** (`test_simplex_solver.py`) — simplex solver tool.
- **Problem solver** (`test_problem_solver.py`) — SciPy/PuLP problem solver.
- **Model validator** (`test_model_validator.py`) — formulation validation tool.
- **LP tool choice** (`test_lp_tool_choice.py`) — LP agent tool-selection behavior.
- **IP tool choice** (`test_ip_tool_choice.py`) — IP agent tool-selection behavior.

### OR tools
- **Problem classifier** (`test_problem_classifier.py`) — problem-type classification tool.
- **Timeline explorer** (`test_timeline_explorer.py`) — OR history timeline tool.

### Utilities
- **Utils** (`test_utils.py`, `test_utils_extended.py`) — general-purpose helper functions.
