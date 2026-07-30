"""
CRUD helper functions for the Complaint and CAPAAction models.
"""
import random
import string
from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from app import models, schemas


def generate_complaint_number(db: Session) -> str:
    """Generates a human-friendly complaint number, e.g. CMP-2026-00001."""
    year = datetime.utcnow().year
    count = db.query(models.Complaint).count() + 1
    suffix = "".join(random.choices(string.digits, k=0))  # kept for extensibility
    return f"CMP-{year}-{count:05d}{suffix}"


def create_complaint(db: Session, complaint_in: schemas.ComplaintCreate) -> models.Complaint:
    complaint = models.Complaint(**complaint_in.model_dump())
    complaint.complaint_number = generate_complaint_number(db)
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


def get_complaint(db: Session, complaint_id: str) -> Optional[models.Complaint]:
    return db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()


def list_complaints(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
) -> List[models.Complaint]:
    q = db.query(models.Complaint)
    if status:
        q = q.filter(models.Complaint.status == status)
    if severity:
        q = q.filter(models.Complaint.severity == severity)
    if risk_level:
        q = q.filter(models.Complaint.ai_risk_level == risk_level)
    if search:
        like = f"%{search}%"
        q = q.filter(
            (models.Complaint.customer_name.ilike(like))
            | (models.Complaint.product_name.ilike(like))
            | (models.Complaint.description.ilike(like))
            | (models.Complaint.complaint_number.ilike(like))
        )
    return q.order_by(models.Complaint.created_at.desc()).offset(skip).limit(limit).all()


def count_complaints(db: Session) -> int:
    return db.query(models.Complaint).count()


def update_complaint(db: Session, complaint: models.Complaint, updates: schemas.ComplaintUpdate) -> models.Complaint:
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(complaint, field, value)
    complaint.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(complaint)
    return complaint


def delete_complaint(db: Session, complaint: models.Complaint) -> None:
    db.delete(complaint)
    db.commit()


def apply_ai_analysis(db: Session, complaint: models.Complaint, analysis: schemas.AIAnalyzeResult) -> models.Complaint:
    complaint.ai_summary = analysis.summary
    complaint.ai_risk_level = analysis.risk_level
    complaint.ai_risk_score = analysis.risk_score
    complaint.ai_risk_rationale = analysis.risk_rationale
    complaint.ai_root_cause_suggestion = analysis.root_cause_suggestion
    complaint.ai_capa_recommendation = analysis.capa_recommendation
    complaint.ai_completeness_score = analysis.completeness_score
    complaint.ai_missing_fields = analysis.missing_fields
    complaint.ai_is_duplicate = analysis.is_duplicate
    complaint.ai_duplicate_of = analysis.duplicate_of
    complaint.ai_duplicate_rationale = analysis.duplicate_rationale
    complaint.ai_extracted_fields = analysis.extracted_fields
    complaint.ai_analysis_complete = True
    complaint.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(complaint)
    return complaint


def add_capa(db: Session, complaint_id: str, capa_in: schemas.CAPAActionCreate) -> models.CAPAAction:
    capa = models.CAPAAction(complaint_id=complaint_id, **capa_in.model_dump())
    db.add(capa)
    db.commit()
    db.refresh(capa)
    return capa


def list_recent_complaints_for_duplicate_check(db: Session, limit: int = 25) -> List[models.Complaint]:
    return db.query(models.Complaint).order_by(models.Complaint.created_at.desc()).limit(limit).all()
