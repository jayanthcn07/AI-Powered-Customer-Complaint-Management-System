"""
SQLAlchemy engine / session setup. Works with SQLite (default, zero-config
demo mode) as well as MySQL / PostgreSQL when DATABASE_URL is set accordingly.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import get_settings

settings = get_settings()


def _normalize_database_url(url: str) -> str:
    """
    Managed Postgres providers (Render, Heroku, Supabase, etc.) sometimes hand
    out connection strings prefixed with 'postgres://' or plain
    'postgresql://'. SQLAlchemy needs the driver explicitly named
    ('postgresql+psycopg2://') to use the psycopg2 driver we install. This
    rewrites the scheme automatically so a copy-pasted connection string works
    with no manual editing.
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


DATABASE_URL = _normalize_database_url(settings.DATABASE_URL)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# pool_pre_ping checks each connection is alive before using it - hosted
# Postgres free tiers (Supabase, Render, etc.) can silently close idle
# connections, and without this you'd see intermittent
# "connection already closed" errors after the app sits idle for a while.
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()