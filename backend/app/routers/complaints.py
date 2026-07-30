"""
CRUD endpoints for Complaint records + CAPA sub-resource.
"""
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.post("", response_model=schemas.ComplaintOut, status_code=201)
def create_complaint(payload: schemas.ComplaintCreate, db: Session = Depends(get_db)):
    return crud.create_complaint(db, payload)


@router.get("", response_model=List[schemas.ComplaintOut])
def list_complaints(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return crud.list_complaints(db, skip, limit, status, severity, risk_level, search)


@router.get("/stats/summary")
def complaint_stats(db: Session = Depends(get_db)):
    from app import models
    total = crud.count_complaints(db)
    high_risk = db.query(models.Complaint).filter(models.Complaint.ai_risk_level == "High").count()
    open_count = db.query(models.Complaint).filter(models.Complaint.status != "Closed").count()
    duplicates = db.query(models.Complaint).filter(models.Complaint.ai_is_duplicate == True).count()  # noqa: E712
    return {
        "total_complaints": total,
        "high_risk": high_risk,
        "open_complaints": open_count,
        "duplicate_complaints": duplicates,
    }


@router.get("/{complaint_id}", response_model=schemas.ComplaintOut)
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = crud.get_complaint(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@router.patch("/{complaint_id}", response_model=schemas.ComplaintOut)
def update_complaint(complaint_id: str, payload: schemas.ComplaintUpdate, db: Session = Depends(get_db)):
    complaint = crud.get_complaint(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return crud.update_complaint(db, complaint, payload)


@router.delete("/{complaint_id}", status_code=204)
def delete_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = crud.get_complaint(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    crud.delete_complaint(db, complaint)


@router.post("/{complaint_id}/capa", response_model=schemas.CAPAActionOut, status_code=201)
def add_capa_action(complaint_id: str, payload: schemas.CAPAActionCreate, db: Session = Depends(get_db)):
    complaint = crud.get_complaint(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return crud.add_capa(db, complaint_id, payload)
