# Unit Tests

Isolated unit tests that verify individual services and utilities without hitting the database or external APIs. All dependencies are mocked.

## Modules covered

- **Agent routing** — LLM agent selection logic.
- **Auth** — Password hashing and JWT token utilities.
- **Competency service** — Student competency tracking and updates.
- **Conversation service** — Chat conversation management.
- **Exercise progress service** — Exercise attempt tracking and scoring.
- **Grading service** — Answer evaluation logic.
- **LLM response parser** — Structured output parsing from LLM responses.
- **Spaced repetition** — SM-2 algorithm for review scheduling.
- **Strategy selection** — Tutoring strategy selection logic.
- **Utils** — General-purpose helper functions.
