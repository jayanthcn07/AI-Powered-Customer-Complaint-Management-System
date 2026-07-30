"""
Shared state object passed between LangGraph nodes.
"""
from typing import TypedDict, List, Optional, Any


class ComplaintAgentState(TypedDict, total=False):
    # input
    raw_text: str
    existing_complaints: List[dict]  # recent complaints, for duplicate detection context

    # node outputs
    extracted_fields: dict
    summary: str
    completeness_score: float
    missing_fields: List[str]
    risk_level: str
    risk_score: float
    risk_rationale: str
    root_cause_suggestion: str
    capa_recommendation: str
    is_duplicate: bool
    duplicate_of: Optional[str]
    duplicate_rationale: Optional[str]

    # bookkeeping
    errors: List[str]
