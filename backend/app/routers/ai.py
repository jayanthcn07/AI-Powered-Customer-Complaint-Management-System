"""
AI Copilot endpoints. These wrap the LangGraph workflow defined in
app/agents/graph.py and expose it to the frontend:

  POST /api/ai/analyze            - run the workflow on pasted text/email, no DB write
  POST /api/ai/analyze-upload     - same, but accepts a PDF/TXT file upload
  POST /api/ai/analyze-and-log    - run the workflow AND create a Complaint record
                                     from the result (used by "Log Customer Complaint")
"""
import io

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app import crud, schemas
from app.agents.graph import run_complaint_workflow
from app.database import get_db

router = APIRouter(prefix="/api/ai", tags=["ai-copilot"])


def _state_to_result(state: dict) -> schemas.AIAnalyzeResult:
    return schemas.AIAnalyzeResult(
        extracted_fields=state.get("extracted_fields", {}),
        summary=state.get("summary", ""),
        completeness_score=state.get("completeness_score", 0.0),
        missing_fields=state.get("missing_fields", []),
        risk_level=state.get("risk_level", "Medium"),
        risk_score=state.get("risk_score", 50.0),
        risk_rationale=state.get("risk_rationale", ""),
        root_cause_suggestion=state.get("root_cause_suggestion", ""),
        capa_recommendation=state.get("capa_recommendation", ""),
        is_duplicate=state.get("is_duplicate", False),
        duplicate_of=state.get("duplicate_of"),
        duplicate_rationale=state.get("duplicate_rationale"),
    )


def _extract_text_from_pdf(raw_bytes: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(raw_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


@router.post("/analyze", response_model=schemas.AIAnalyzeResult)
def analyze_text(payload: schemas.AIAnalyzeTextRequest, db: Session = Depends(get_db)):
    recent = crud.list_recent_complaints_for_duplicate_check(db)
    existing = [
        {"id": c.id, "product_name": c.product_name, "batch_number": c.batch_number,
         "description": c.description}
        for c in recent
    ]
    final_state = run_complaint_workflow(payload.text, existing)
    return _state_to_result(final_state)


@router.post("/analyze-upload", response_model=schemas.AIAnalyzeResult)
async def analyze_upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    raw_bytes = await file.read()
    if file.filename.lower().endswith(".pdf"):
        try:
            text = _extract_text_from_pdf(raw_bytes)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not parse PDF: {e}")
    else:
        text = raw_bytes.decode("utf-8", errors="ignore")

    if not text.strip():
        raise HTTPException(status_code=400, detail="No extractable text found in uploaded file.")

    recent = crud.list_recent_complaints_for_duplicate_check(db)
    existing = [
        {"id": c.id, "product_name": c.product_name, "batch_number": c.batch_number,
         "description": c.description}
        for c in recent
    ]
    final_state = run_complaint_workflow(text, existing)
    result = _state_to_result(final_state)
    return result


@router.post("/analyze-and-log", response_model=schemas.ComplaintOut, status_code=201)
def analyze_and_log(payload: schemas.AIAnalyzeTextRequest, db: Session = Depends(get_db)):
    """Runs the full AI Copilot workflow, then creates a Complaint row pre-filled
    from the extracted fields and stamped with the AI risk assessment - this powers
    the 'Log Customer Complaint' + 'AI Copilot Risk Assessment' flow in the demo."""
    recent = crud.list_recent_complaints_for_duplicate_check(db)
    existing = [
        {"id": c.id, "product_name": c.product_name, "batch_number": c.batch_number,
         "description": c.description}
        for c in recent
    ]
    final_state = run_complaint_workflow(payload.text, existing)
    fields = final_state.get("extracted_fields", {})

    complaint_in = schemas.ComplaintCreate(
        customer_name=fields.get("customer_name") or "Unknown Customer",
        customer_email=fields.get("customer_email"),
        customer_contact=fields.get("customer_contact"),
        source_channel="AI Copilot Ingestion",
        product_name=fields.get("product_name") or "Unknown Product",
        product_code=fields.get("product_code"),
        batch_number=fields.get("batch_number"),
        manufacturing_date=fields.get("manufacturing_date"),
        expiry_date=fields.get("expiry_date"),
        market=fields.get("market"),
        complaint_type=fields.get("complaint_type") or "Other",
        severity=fields.get("severity") or "Minor",
        description=fields.get("description") or payload.text[:400],
        raw_source_text=payload.text,
    )
    complaint = crud.create_complaint(db, complaint_in)
    analysis_result = _state_to_result(final_state)
    complaint = crud.apply_ai_analysis(db, complaint, analysis_result)
    return complaint


@router.post("/reanalyze/{complaint_id}", response_model=schemas.ComplaintOut)
def reanalyze_complaint(complaint_id: str, db: Session = Depends(get_db)):
    """Re-runs the AI Copilot workflow against an existing complaint's description,
    e.g. after a manual edit, and refreshes its AI fields."""
    complaint = crud.get_complaint(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    recent = [c for c in crud.list_recent_complaints_for_duplicate_check(db) if c.id != complaint_id]
    existing = [
        {"id": c.id, "product_name": c.product_name, "batch_number": c.batch_number,
         "description": c.description}
        for c in recent
    ]
    source_text = complaint.raw_source_text or (
        f"Customer: {complaint.customer_name}\nProduct: {complaint.product_name}\n"
        f"Batch: {complaint.batch_number}\nDescription: {complaint.description}"
    )
    final_state = run_complaint_workflow(source_text, existing)
    analysis_result = _state_to_result(final_state)
    complaint = crud.apply_ai_analysis(db, complaint, analysis_result)
    return complaint
