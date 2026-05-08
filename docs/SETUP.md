# Local Development Setup

> Looking to deploy to a server? See [deploy_guide.md](deploy_guide.md) for the DigitalOcean walkthrough.

## Prerequisites

- Python 3.13+
- PostgreSQL 16+
- An LLM API key (Google Gemini, OpenAI, or Anthropic)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/JorgeMoragaCalvo/theses-impl.git
cd theses-impl
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
```

Edit `.env` and fill in the required values:
- `DATABASE_URL` — PostgreSQL connection string
- `SECRET_KEY` — generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `LLM_PROVIDER` — `gemini` (default), `openai`, or `anthropic`
- The corresponding API key (`GOOGLE_API_KEY`, `OPENAI_API_KEY`, or `ANTHROPIC_API_KEY`)

5. Initialize the database:

```bash
python backend/init_db.py
```

## Running (Local Development)

**Quick start (Windows):** from the project root, run:

```bat
.\start.bat
```

This launches the FastAPI backend in a new terminal, waits ~45s for it to come up, then starts the Streamlit frontend.

### Or start each service manually

**Backend (FastAPI):**

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` (docs at `/docs`).

**Frontend (Streamlit):**

```bash
cd frontend
streamlit run app.py
```

The UI will be available at `http://localhost:8501`.

## Running (Docker Compose)

For a production-like setup with PostgreSQL, Nginx reverse proxy, and HTTPS:

```bash
# Generate self-signed SSL certs (or provide your own in nginx/ssl/)
bash nginx/ssl/generate-certs.sh

# Copy and configure environment
cp .env.example .env
# Edit .env with your values

# Build and start all services
docker compose up --build
```

This starts four services: **PostgreSQL** → **Backend** → **Frontend** → **Nginx** (ports 80/443).