# Backend - AI-Powered Customer Complaint Management System

FastAPI + LangGraph + Groq + SQLAlchemy service for the pharmaceutical
Customer Complaint QMS module. See the root `README.md` for the full
project overview and deployment instructions - this file covers backend
specifics only.

## Local setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set GROQ_API_KEY (see root README for where to get one)

# Optional: load 5 realistic sample complaints through the real AI pipeline
python -m app.sample_data.seed

uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs
Health check: http://localhost:8000/api/health

## Project layout

```
app/
  main.py            FastAPI app, CORS, router registration
  config.py          Settings loaded from .env
  database.py        SQLAlchemy engine/session
  models.py          Complaint / CAPAAction ORM models
  schemas.py         Pydantic request/response schemas
  crud.py            DB access helpers
  routers/
    complaints.py    CRUD + stats endpoints
    ai.py            AI Copilot / LangGraph endpoints
  agents/
    state.py         LangGraph state schema
    nodes.py          extract / completeness / duplicate / risk / root
                       cause / CAPA / summary node implementations
    graph.py          Assembles + compiles the LangGraph StateGraph
    llm.py            Groq (ChatGroq) client wrapper
  sample_data/
    complaints/*.txt  Sample complaint emails/documents for the demo
    seed.py           Loads sample complaints through the live AI pipeline
```

## Notes

- Without `GROQ_API_KEY` set, every AI node automatically falls back to a
  deterministic heuristic implementation, so the API and full LangGraph
  workflow still run end-to-end for local testing/grading. Set the key to
  exercise the real Groq-backed reasoning.
- `DATABASE_URL` defaults to a local SQLite file (zero config). Point it at
  Postgres or MySQL for production - see the root README.
