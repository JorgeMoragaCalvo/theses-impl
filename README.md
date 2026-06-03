<div align="center">

# Multi-Agent Tutor

**Adaptive, multi-agent AI tutoring system for Operations Research and Mathematical Optimization.**
Thesis project — built end-to-end: backend, frontend, AI agents, infra, CI/CD, deployment.

[![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.120%2B-009485?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/) [![LangChain](https://img.shields.io/badge/LangChain-1.0%2B-1c3c3c?style=flat-square&logo=langchain&logoColor=white)](https://www.langchain.com/) [![Streamlit](https://img.shields.io/badge/Streamlit-1.50%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/) [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/) [![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)

[![ChatGPT](https://custom-icon-badges.demolab.com/badge/ChatGPT-74aa9c?logo=openai&logoColor=white)](#) [![Claude](https://img.shields.io/badge/Claude-D97757?logo=claude&logoColor=fff)](#) [![Google Gemini](https://img.shields.io/badge/Google%20Gemini-886FBF?logo=googlegemini&logoColor=fff)](#)

</div>

---

## 🚀 Live Deployment

Deployed on **DigitalOcean** at `http://192.241.142.33` via Docker Compose:
**PostgreSQL → FastAPI (Gunicorn/UvicornWorker) → Streamlit → Nginx** with HTTPS (TLS 1.2+), HSTS, and rate limiting.

Step-by-step deployment instructions (Droplet creation → Docker → SSL certs → `.env` → bring-up): [Deploy Guide](docs/deploy_guide.md).

## 🎬 Demo

<!-- TODO: replace with embedded demo video (login → topic selection → adaptive chat → assessment submission → progress dashboard) -->
*Demo walkthrough video — coming soon.*

---

## ✨ Highlights

- **Multi-agent AI system** — $5$ specialist tutors (Linear, Integer, Nonlinear Programming, Mathematical Modeling, Operations Research) inheriting a shared `BaseAgent`. Built on LangChain with tool-calling so agents can solve, plot, and validate during the conversation.
- **Adaptive pedagogy engine** — keyword-based confusion detection, dynamic switching between $7$ explanation strategies, SM-2 spaced repetition for review scheduling, and Bloom-taxonomy competency tracking per concept.
- **LLM provider abstraction** — single adapter over Google Gemini, OpenAI, and Anthropic, switchable via `LLM_PROVIDER` env var.
- **Domain tooling for optimization** — SciPy/PuLP solvers, matplotlib feasible-region plots, and model validators wired as LangChain tools the agents invoke autonomously.
- **Production-grade infra** — multi-stage Docker builds, non-root containers, Nginx reverse proxy with HTTPS + rate limiting, Prometheus + Sentry observability, GitHub Actions CI with `pip-audit` and CodeQL.
- **Auth & RBAC** — JWT (python-jose), bcrypt password hashing, USER/ADMIN roles, admin dashboard with usage analytics.

---

## 🧠 How the AI works

- A specialist agent is selected from an `AGENT_REGISTRY` based on the topic the student picks.
- `BaseAgent` injects **adaptive context** into every system prompt: detected confusion signals, the chosen explanation strategy, and the student's spaced-repetition review queue.
- A **LangChain tool-calling loop** lets agents call solvers, region visualizers, and exercise validators mid-conversation — answers can include computed optima and rendered plots, not just prose.
- **LLM-based auto-grading** for assessments, with admin override. Three difficulty levels (beginner / intermediate / advanced); Chilean 1.0–7.0 grading scale.
- UI is in **Spanish** — built for Chilean university students; deliberate, not a limitation.

---

## 🏗️ Architecture

<details>
<summary><b>Backend</b> — Layered FastAPI service over SQLAlchemy + PostgreSQL</summary>

```
API Layer (FastAPI)  →  Business Logic (Services / Agents)  →  Data Access (SQLAlchemy)  →  PostgreSQL
```

| Pattern              | Where                          | Purpose                                                          |
|----------------------|--------------------------------|------------------------------------------------------------------|
| Template Method      | `agents/base_agent.py`         | Shared adaptive logic; subclasses override system prompt & tools |
| Registry / Factory   | `main.py` (`AGENT_REGISTRY`)   | Maps topics to agent factory functions                           |
| Strategy             | `base_agent.py`                | 7 interchangeable explanation strategies                         |
| Adapter              | `services/llm_service.py`      | Unified interface across Gemini / OpenAI / Anthropic             |

JWT auth, role-based authorization, Pydantic validation on every endpoint, CORS + lifespan middleware, JSON columns for flexible metadata.
</details>

<details>
<summary><b>Frontend</b> — Streamlit multipage app with singleton API client</summary>

File-based routing across `pages/1_chat.py`, `2_assessment.py`, `3_progress.py`, `4_admin.py`. Singleton API client (`utils/api_client.py`) auto-injects JWT and triggers logout on 401. State managed via `st.session_state`.
</details>

---

## 📊 Observability & Monitoring

Three layers wired in: **Prometheus** (HTTP latency, request rate, in-flight requests, status codes), **Sentry** (exceptions, traces, releases), and a **`/health`** liveness probe used by Docker/DigitalOcean. `/metrics` is firewalled at the Nginx layer.

<!-- TODO: add Prometheus/Grafana screenshots — request rate, p95 latency, error rate -->
<!-- TODO: add Sentry dashboard screenshot -->
*Live dashboard screenshots — coming soon.*

---

## 🧪 Quality

- **326 unit tests** (pytest + fixtures in `conftest.py`)
- **ruff** linting (E, W, F, I, B, UP rule sets)
- **GitHub Actions CI** with `pip-audit` (dependency CVE scan) and **CodeQL** (static analysis)
- bcrypt password hashing, JWT expiration, no PII sent to Sentry

---

## 📂 Project Layout

```
backend/app/
  main.py            FastAPI app, agent registry, lifespan
  agents/            5 specialist tutors over a shared BaseAgent
  services/          LLM, conversation, assessment, grading, competency, spaced repetition
  tools/             LangChain tools: solvers, visualizers, validators
frontend/
  app.py + pages/    Streamlit MPA (chat / assessment / progress / admin)
data/course_materials/   Pre-built exercises per topic
nginx/                   Reverse proxy + TLS configuration
```

---

## 🛠️ Getting Started

For local development setup (Python venv, Docker Compose, env vars), see **[docs/SETUP.md](docs/SETUP.md)**.

## 📋 Roadmap

5-phase plan to lift pedagogical effectiveness from 3/5 → 4–5/5 maturity — see [docs/notes/todo-details.md](docs/notes/todo-details.md).

---

## 👤 Author

**Jorge Moraga Calvo** · Universidad de Santiago de Chile · jorge.moraga.c@usach.cl
