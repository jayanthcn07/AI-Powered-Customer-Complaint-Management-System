"""
FastAPI application entrypoint.

Run locally with:
    uvicorn app.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import complaints, ai

settings = get_settings()

# Create tables on startup (SQLite demo mode / first Postgres boot).
# For production Postgres/MySQL, prefer Alembic migrations instead.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Customer Complaint Management System for pharmaceutical "
                 "manufacturing (API/FDF) - FastAPI + LangGraph + Groq backend.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(complaints.router)
app.include_router(ai.router)


@app.get("/api/health", tags=["system"])
def health_check():
    return {
        "status": "ok",
        "app_name": settings.APP_NAME,
        "groq_configured": bool(settings.GROQ_API_KEY),
    }


@app.get("/", tags=["system"])
def root():
    return {
        "message": f"{settings.APP_NAME} API",
        "docs": "/docs",
        "health": "/api/health",
    }
