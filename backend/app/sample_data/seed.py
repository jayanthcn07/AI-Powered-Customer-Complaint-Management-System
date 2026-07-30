"""
Seeds the database with realistic sample complaints so the dashboard/UI has
demo data immediately after setup - runs the same LangGraph AI Copilot
workflow used by the live app (falls back to heuristics automatically if
GROQ_API_KEY is not set, so this works with zero configuration).

Usage:
    python -m app.sample_data.seed
"""
import glob
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.database import Base, engine, SessionLocal  # noqa: E402
from app import crud, schemas  # noqa: E402
from app.agents.graph import run_complaint_workflow  # noqa: E402

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "complaints")


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if crud.count_complaints(db) > 0:
            print("Database already has complaints - skipping seed. "
                  "Delete complaints.db (or truncate tables) to reseed.")
            return

        files = sorted(glob.glob(os.path.join(SAMPLE_DIR, "*.txt")))
        print(f"Seeding {len(files)} sample complaints...")

        for path in files:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

            existing = crud.list_recent_complaints_for_duplicate_check(db)
            existing_dicts = [
                {"id": c.id, "product_name": c.product_name, "batch_number": c.batch_number,
                 "description": c.description}
                for c in existing
            ]
            state = run_complaint_workflow(text, existing_dicts)
            fields = state.get("extracted_fields", {})

            complaint_in = schemas.ComplaintCreate(
                customer_name=fields.get("customer_name") or "Unknown Customer",
                customer_email=fields.get("customer_email"),
                customer_contact=fields.get("customer_contact"),
                source_channel="Sample Data Seed",
                product_name=fields.get("product_name") or "Unknown Product",
                product_code=fields.get("product_code"),
                batch_number=fields.get("batch_number"),
                manufacturing_date=fields.get("manufacturing_date"),
                expiry_date=fields.get("expiry_date"),
                market=fields.get("market"),
                complaint_type=fields.get("complaint_type") or "Other",
                severity=fields.get("severity") or "Minor",
                description=fields.get("description") or text[:400],
                raw_source_text=text,
            )
            complaint = crud.create_complaint(db, complaint_in)

            analysis = schemas.AIAnalyzeResult(
                extracted_fields=fields,
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
            crud.apply_ai_analysis(db, complaint, analysis)
            print(f"  + {complaint.complaint_number}: {complaint.product_name} "
                  f"({complaint.ai_risk_level})")

        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
