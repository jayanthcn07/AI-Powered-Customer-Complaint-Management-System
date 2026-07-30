"""
Pydantic request/response schemas.
"""
from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel, Field, ConfigDict

from app.models import ComplaintType, ComplaintSeverity, ComplaintStatus, RiskLevel


# ---------------------------------------------------------------------------
# CAPA
# ---------------------------------------------------------------------------
class CAPAActionBase(BaseModel):
    action_type: str = "Corrective"
    description: str
    owner: Optional[str] = None
    due_date: Optional[str] = None
    status: str = "Open"


class CAPAActionCreate(CAPAActionBase):
    pass


class CAPAActionOut(CAPAActionBase):
    id: str
    complaint_id: str
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Complaint
# ---------------------------------------------------------------------------
class ComplaintBase(BaseModel):
    customer_name: str
    customer_email: Optional[str] = None
    customer_contact: Optional[str] = None
    source_channel: Optional[str] = "Manual Entry"

    product_name: str
    product_code: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    market: Optional[str] = None

    complaint_type: ComplaintType = ComplaintType.OTHER
    severity: ComplaintSeverity = ComplaintSeverity.MINOR
    description: str
    status: ComplaintStatus = ComplaintStatus.NEW


class ComplaintCreate(ComplaintBase):
    raw_source_text: Optional[str] = None
    attachment_filename: Optional[str] = None


class ComplaintUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_contact: Optional[str] = None
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    market: Optional[str] = None
    complaint_type: Optional[ComplaintType] = None
    severity: Optional[ComplaintSeverity] = None
    description: Optional[str] = None
    status: Optional[ComplaintStatus] = None


class ComplaintOut(ComplaintBase):
    id: str
    complaint_number: Optional[str] = None
    date_received: datetime
    raw_source_text: Optional[str] = None
    attachment_filename: Optional[str] = None

    ai_summary: Optional[str] = None
    ai_risk_level: Optional[RiskLevel] = None
    ai_risk_score: Optional[float] = None
    ai_risk_rationale: Optional[str] = None
    ai_root_cause_suggestion: Optional[str] = None
    ai_capa_recommendation: Optional[str] = None
    ai_completeness_score: Optional[float] = None
    ai_missing_fields: Optional[List[str]] = None
    ai_is_duplicate: Optional[bool] = False
    ai_duplicate_of: Optional[str] = None
    ai_duplicate_rationale: Optional[str] = None
    ai_extracted_fields: Optional[Any] = None
    ai_analysis_complete: Optional[bool] = False

    created_at: datetime
    updated_at: datetime
    capas: List[CAPAActionOut] = []

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# AI Copilot
# ---------------------------------------------------------------------------
class AIAnalyzeTextRequest(BaseModel):
    """Free-text or pasted-email complaint content to be run through the
    LangGraph AI Copilot workflow (no DB row created)."""
    text: str = Field(..., min_length=5)


class AIAnalyzeResult(BaseModel):
    extracted_fields: dict
    summary: str
    completeness_score: float
    missing_fields: List[str]
    risk_level: RiskLevel
    risk_score: float
    risk_rationale: str
    root_cause_suggestion: str
    capa_recommendation: str
    is_duplicate: bool
    duplicate_of: Optional[str] = None
    duplicate_rationale: Optional[str] = None


class HealthOut(BaseModel):
    status: str
    app_name: str
    groq_configured: bool
