"""
ORM models for the Customer Complaint Management System.

The `Complaint` model captures the fields typically found in a
pharmaceutical QMS "Customer Complaint" record (customer/product/batch
details) plus the outputs produced by the LangGraph AI Copilot
(risk classification, root cause suggestion, CAPA recommendation,
completeness check, duplicate detection, summary).
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, DateTime, Enum, Float, Boolean, JSON, ForeignKey
)
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class ComplaintType(str, enum.Enum):
    QUALITY_DEFECT = "Quality Defect"
    ADVERSE_EVENT = "Adverse Event"
    PACKAGING_LABELING = "Packaging/Labeling"
    PRODUCT_EFFICACY = "Product Efficacy"
    CONTAMINATION = "Contamination"
    DELIVERY_LOGISTICS = "Delivery/Logistics"
    OTHER = "Other"


class ComplaintSeverity(str, enum.Enum):
    CRITICAL = "Critical"
    MAJOR = "Major"
    MINOR = "Minor"


class ComplaintStatus(str, enum.Enum):
    NEW = "New"
    UNDER_INVESTIGATION = "Under Investigation"
    CAPA_INITIATED = "CAPA Initiated"
    CLOSED = "Closed"


class RiskLevel(str, enum.Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    complaint_number = Column(String(32), unique=True, index=True)

    # --- Customer / source info ---------------------------------------
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=True)
    customer_contact = Column(String(64), nullable=True)
    source_channel = Column(String(64), default="Manual Entry")  # Email, PDF Upload, Manual Entry, Portal

    # --- Product / batch info -----------------------------------------
    product_name = Column(String(255), nullable=False)
    product_code = Column(String(64), nullable=True)
    batch_number = Column(String(64), nullable=True)
    manufacturing_date = Column(String(32), nullable=True)
    expiry_date = Column(String(32), nullable=True)
    market = Column(String(128), nullable=True)  # API / FDF / country market

    # --- Complaint details ----------------------------------------------
    complaint_type = Column(Enum(ComplaintType), default=ComplaintType.OTHER)
    severity = Column(Enum(ComplaintSeverity), default=ComplaintSeverity.MINOR)
    description = Column(Text, nullable=False)
    date_received = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.NEW)

    # --- Raw source content (for AI ingestion demo) --------------------
    raw_source_text = Column(Text, nullable=True)
    attachment_filename = Column(String(255), nullable=True)

    # --- AI Copilot outputs ---------------------------------------------
    ai_summary = Column(Text, nullable=True)
    ai_risk_level = Column(Enum(RiskLevel), nullable=True)
    ai_risk_score = Column(Float, nullable=True)
    ai_risk_rationale = Column(Text, nullable=True)
    ai_root_cause_suggestion = Column(Text, nullable=True)
    ai_capa_recommendation = Column(Text, nullable=True)
    ai_completeness_score = Column(Float, nullable=True)
    ai_missing_fields = Column(JSON, nullable=True)  # list[str]
    ai_is_duplicate = Column(Boolean, default=False)
    ai_duplicate_of = Column(String(36), nullable=True)
    ai_duplicate_rationale = Column(Text, nullable=True)
    ai_extracted_fields = Column(JSON, nullable=True)  # raw structured extraction
    ai_analysis_complete = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    capas = relationship("CAPAAction", back_populates="complaint", cascade="all, delete-orphan")


class CAPAAction(Base):
    """Individual Corrective / Preventive Action items linked to a complaint."""
    __tablename__ = "capa_actions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    complaint_id = Column(String(36), ForeignKey("complaints.id"), nullable=False)
    action_type = Column(String(16), default="Corrective")  # Corrective / Preventive
    description = Column(Text, nullable=False)
    owner = Column(String(128), nullable=True)
    due_date = Column(String(32), nullable=True)
    status = Column(String(32), default="Open")

    complaint = relationship("Complaint", back_populates="capas")
