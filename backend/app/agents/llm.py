"""
Thin wrapper around ChatGroq so the rest of the app doesn't need to know
about model names / API keys directly.

Primary model: gemma2-9b-it (fast, cheap - used for most nodes)
Context model: llama-3.3-70b-versatile (larger context / reasoning - used
               for the more nuanced root-cause / CAPA reasoning step)
"""
import json
import re
from functools import lru_cache

from langchain_groq import ChatGroq

from app.config import get_settings

settings = get_settings()


@lru_cache
def get_primary_llm() -> ChatGroq:
    """gemma2-9b-it — fast extraction / classification tasks."""
    return ChatGroq(
        model=settings.GROQ_PRIMARY_MODEL,
        api_key=settings.GROQ_API_KEY or "placeholder",
        temperature=0.1,
    )


@lru_cache
def get_context_llm() -> ChatGroq:
    """llama-3.3-70b-versatile — used for reasoning-heavy steps (root cause / CAPA)."""
    return ChatGroq(
        model=settings.GROQ_CONTEXT_MODEL,
        api_key=settings.GROQ_API_KEY or "placeholder",
        temperature=0.2,
    )


def extract_json(raw: str) -> dict:
    """
    LLMs occasionally wrap JSON in markdown fences or add stray prose.
    This pulls out the first {...} block and parses it defensively.
    """
    raw = raw.strip()
    raw = re.sub(r"^```(json)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in LLM output: {raw[:200]}")
    return json.loads(match.group(0))
