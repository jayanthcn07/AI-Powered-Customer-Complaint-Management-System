"""
LangGraph node implementations for the Customer Complaint AI Copilot.

Pipeline:
  extract_info -> completeness_check -> duplicate_detection
                -> risk_classification -> root_cause_recommendation
                -> capa_recommendation -> summarize -> END

Every node calls the Groq LLM (gemma2-9b-it for lighter tasks,
llama-3.3-70b-versatile for the reasoning-heavy root-cause/CAPA step).
If no GROQ_API_KEY is configured (or the call fails for any reason,
e.g. offline demo / rate limit), each node transparently falls back to a
deterministic heuristic implementation so the workflow always completes
end-to-end. This keeps local development / grading frictionless while
still exercising the full LangGraph + Groq path when a real key is set.
"""
import re
from datetime import datetime
from typing import List

from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.llm import get_primary_llm, get_context_llm, extract_json
from app.agents.state import ComplaintAgentState
from app.config import get_settings

settings = get_settings()

REQUIRED_FIELDS = [
    "customer_name", "product_name", "batch_number", "complaint_type",
    "description", "manufacturing_date",
]


def _llm_configured() -> bool:
    return bool(settings.GROQ_API_KEY)


# ---------------------------------------------------------------------------
# 1. Extraction
# ---------------------------------------------------------------------------
def extract_info(state: ComplaintAgentState) -> ComplaintAgentState:
    text = state["raw_text"]
    extracted = None
    if _llm_configured():
        try:
            llm = get_primary_llm()
            prompt = (
                "You are a pharmaceutical QMS assistant. Extract structured fields "
                "from the customer complaint text below. Return ONLY a JSON object "
                "with these keys (use null if not present): customer_name, "
                "customer_email, customer_contact, product_name, product_code, "
                "batch_number, manufacturing_date, expiry_date, market, "
                "complaint_type (one of: Quality Defect, Adverse Event, "
                "Packaging/Labeling, Product Efficacy, Contamination, "
                "Delivery/Logistics, Other), severity (Critical, Major, Minor), "
                "description (a clean 1-3 sentence restatement of the issue).\n\n"
                f"COMPLAINT TEXT:\n{text}"
            )
            resp = llm.invoke([SystemMessage(content="Respond with strict JSON only."),
                                HumanMessage(content=prompt)])
            extracted = extract_json(resp.content)
        except Exception as e:
            state.setdefault("errors", []).append(f"extract_info LLM fallback: {e}")

    if extracted is None:
        extracted = _heuristic_extract(text)

    state["extracted_fields"] = extracted
    return state


def _heuristic_extract(text: str) -> dict:
    """Regex-based fallback extraction used when no LLM is available."""
    def find(pattern, default=None):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m else default

    return {
        "customer_name": find(r"(?:customer|from|name)\s*[:\-]\s*(.+)"),
        "customer_email": find(r"([\w\.-]+@[\w\.-]+\.\w+)"),
        "customer_contact": find(r"(?:phone|contact|mobile)\s*[:\-]\s*([\d\+\-\s]{6,})"),
        "product_name": find(r"(?:product|drug|medicine)\s*[:\-]\s*(.+)"),
        "product_code": find(r"(?:product code|sku)\s*[:\-]\s*([\w\-]+)"),
        "batch_number": find(r"(?:batch(?: no\.?| number)?)\s*[:\-]\s*([\w\-]+)"),
        "manufacturing_date": find(r"(?:mfg\.?\s*date|manufacturing date)\s*[:\-]\s*([\d/\-]+)"),
        "expiry_date": find(r"(?:exp\.?\s*date|expiry date)\s*[:\-]\s*([\d/\-]+)"),
        "market": find(r"(?:market|country|region)\s*[:\-]\s*(.+)"),
        "complaint_type": "Quality Defect" if re.search(r"defect|discolor|broken|damage", text, re.I)
            else "Adverse Event" if re.search(r"reaction|side effect|adverse", text, re.I)
            else "Packaging/Labeling" if re.search(r"packag|label", text, re.I)
            else "Other",
        "severity": "Critical" if re.search(r"critical|severe|hospital|death", text, re.I)
            else "Major" if re.search(r"major|significant", text, re.I) else "Minor",
        "description": text.strip()[:400],
    }


# ---------------------------------------------------------------------------
# 2. Completeness Checker (bonus feature)
# ---------------------------------------------------------------------------
def completeness_check(state: ComplaintAgentState) -> ComplaintAgentState:
    fields = state["extracted_fields"]
    missing = [f for f in REQUIRED_FIELDS if not fields.get(f)]
    score = round(100 * (len(REQUIRED_FIELDS) - len(missing)) / len(REQUIRED_FIELDS), 1)
    state["completeness_score"] = score
    state["missing_fields"] = missing
    return state


# ---------------------------------------------------------------------------
# 3. Duplicate Complaint Detection (bonus feature)
# ---------------------------------------------------------------------------
def duplicate_detection(state: ComplaintAgentState) -> ComplaintAgentState:
    fields = state["extracted_fields"]
    existing = state.get("existing_complaints", [])
    is_dup, dup_of, rationale = False, None, None

    if existing:
        if _llm_configured():
            try:
                llm = get_primary_llm()
                candidates_text = "\n".join(
                    f"- id={c['id']} | product={c.get('product_name')} | batch={c.get('batch_number')} | "
                    f"desc={c.get('description', '')[:150]}"
                    for c in existing
                )
                prompt = (
                    "New complaint:\n"
                    f"product={fields.get('product_name')} | batch={fields.get('batch_number')} | "
                    f"desc={fields.get('description', '')[:200]}\n\n"
                    f"Existing recent complaints:\n{candidates_text}\n\n"
                    "Does the new complaint appear to be a duplicate/near-duplicate of any existing "
                    "complaint (same product+batch and materially the same issue)? "
                    "Return ONLY JSON: {\"is_duplicate\": bool, \"duplicate_of\": \"<id or null>\", "
                    "\"rationale\": \"<one sentence>\"}"
                )
                resp = llm.invoke([SystemMessage(content="Respond with strict JSON only."),
                                    HumanMessage(content=prompt)])
                result = extract_json(resp.content)
                is_dup = bool(result.get("is_duplicate"))
                dup_of = result.get("duplicate_of")
                rationale = result.get("rationale")
            except Exception as e:
                state.setdefault("errors", []).append(f"duplicate_detection LLM fallback: {e}")
                is_dup, dup_of, rationale = _heuristic_duplicate(fields, existing)
        else:
            is_dup, dup_of, rationale = _heuristic_duplicate(fields, existing)

    state["is_duplicate"] = is_dup
    state["duplicate_of"] = dup_of if is_dup else None
    state["duplicate_rationale"] = rationale
    return state


def _heuristic_duplicate(fields: dict, existing: List[dict]):
    batch = (fields.get("batch_number") or "").lower().strip()
    product = (fields.get("product_name") or "").lower().strip()
    if not batch and not product:
        return False, None, None
    for c in existing:
        c_batch = (c.get("batch_number") or "").lower().strip()
        c_product = (c.get("product_name") or "").lower().strip()
        if batch and product and batch == c_batch and product == c_product:
            return True, c["id"], "Same product and batch number as an existing complaint."
    return False, None, None


# ---------------------------------------------------------------------------
# 4. AI Risk Classification
# ---------------------------------------------------------------------------
def risk_classification(state: ComplaintAgentState) -> ComplaintAgentState:
    fields = state["extracted_fields"]
    result = None
    if _llm_configured():
        try:
            llm = get_primary_llm()
            prompt = (
                "You are a pharmaceutical QMS risk assessment assistant. Given this "
                f"complaint: severity={fields.get('severity')}, type={fields.get('complaint_type')}, "
                f"description=\"{fields.get('description')}\", classify the patient/business risk. "
                "Return ONLY JSON: {\"risk_level\": \"High|Medium|Low\", \"risk_score\": <0-100 number>, "
                "\"rationale\": \"<1-2 sentence rationale>\"}"
            )
            resp = llm.invoke([SystemMessage(content="Respond with strict JSON only."),
                                HumanMessage(content=prompt)])
            result = extract_json(resp.content)
        except Exception as e:
            state.setdefault("errors", []).append(f"risk_classification LLM fallback: {e}")

    if result is None:
        result = _heuristic_risk(fields)

    state["risk_level"] = result.get("risk_level", "Medium")
    state["risk_score"] = float(result.get("risk_score", 50))
    state["risk_rationale"] = result.get("rationale", "")
    return state


def _heuristic_risk(fields: dict) -> dict:
    severity = (fields.get("severity") or "Minor").lower()
    ctype = (fields.get("complaint_type") or "").lower()
    if severity == "critical" or "adverse" in ctype or "contamination" in ctype:
        return {"risk_level": "High", "risk_score": 85,
                "rationale": "Critical severity or safety-related complaint type (adverse event/contamination) "
                             "indicates potential patient safety impact."}
    if severity == "major":
        return {"risk_level": "Medium", "risk_score": 55,
                "rationale": "Major severity quality issue with possible product performance impact."}
    return {"risk_level": "Low", "risk_score": 20,
            "rationale": "Minor severity issue with limited patient/business impact."}


# ---------------------------------------------------------------------------
# 5. Root Cause Recommendation (bonus feature) - uses larger context model
# ---------------------------------------------------------------------------
def root_cause_recommendation(state: ComplaintAgentState) -> ComplaintAgentState:
    fields = state["extracted_fields"]
    suggestion = None
    if _llm_configured():
        try:
            llm = get_context_llm()
            prompt = (
                "You are a pharmaceutical manufacturing quality expert (API/FDF). "
                f"Complaint type: {fields.get('complaint_type')}. "
                f"Description: {fields.get('description')}. "
                "Suggest the most likely root cause category (e.g. raw material variability, "
                "equipment malfunction, process deviation, packaging line issue, storage/transport "
                "condition, labeling error, human error) and a brief 2-3 sentence explanation. "
                "Return ONLY JSON: {\"root_cause\": \"<short text>\"}"
            )
            resp = llm.invoke([SystemMessage(content="Respond with strict JSON only."),
                                HumanMessage(content=prompt)])
            suggestion = extract_json(resp.content).get("root_cause")
        except Exception as e:
            state.setdefault("errors", []).append(f"root_cause_recommendation LLM fallback: {e}")

    if not suggestion:
        suggestion = _heuristic_root_cause(fields)

    state["root_cause_suggestion"] = suggestion
    return state


def _heuristic_root_cause(fields: dict) -> str:
    ctype = (fields.get("complaint_type") or "").lower()
    mapping = {
        "packaging": "Likely packaging/labeling line deviation - recommend reviewing line clearance and "
                     "label reconciliation records for the referenced batch.",
        "adverse": "Potential formulation or contamination issue - recommend reviewing batch manufacturing "
                    "records, in-process controls, and stability data.",
        "contamination": "Possible cross-contamination or environmental control failure - recommend reviewing "
                          "cleaning validation and environmental monitoring data.",
        "efficacy": "Possible raw material variability or process deviation affecting potency - recommend "
                    "reviewing raw material COAs and process parameters for the batch.",
        "defect": "Likely equipment malfunction or process deviation during manufacturing - recommend "
                  "reviewing batch manufacturing records and equipment maintenance logs.",
    }
    for key, val in mapping.items():
        if key in ctype:
            return val
    return ("Insufficient specificity to isolate a single root cause category - recommend a standard "
            "batch record review and customer follow-up for additional detail.")


# ---------------------------------------------------------------------------
# 6. CAPA Recommendation (bonus feature)
# ---------------------------------------------------------------------------
def capa_recommendation(state: ComplaintAgentState) -> ComplaintAgentState:
    fields = state["extracted_fields"]
    root_cause = state.get("root_cause_suggestion", "")
    capa = None
    if _llm_configured():
        try:
            llm = get_context_llm()
            prompt = (
                "Given this pharmaceutical customer complaint and its likely root cause, propose a concise "
                "CAPA (Corrective and Preventive Action) plan with one corrective action and one preventive "
                f"action.\nComplaint: {fields.get('description')}\nRoot cause: {root_cause}\n"
                "Return ONLY JSON: {\"corrective_action\": \"<text>\", \"preventive_action\": \"<text>\"}"
            )
            resp = llm.invoke([SystemMessage(content="Respond with strict JSON only."),
                                HumanMessage(content=prompt)])
            result = extract_json(resp.content)
            capa = (f"Corrective: {result.get('corrective_action')}\n"
                    f"Preventive: {result.get('preventive_action')}")
        except Exception as e:
            state.setdefault("errors", []).append(f"capa_recommendation LLM fallback: {e}")

    if not capa:
        capa = (
            "Corrective: Investigate and disposition the affected batch; issue customer response with "
            "findings.\n"
            "Preventive: Update SOP/training or add an in-process check to prevent recurrence, and "
            "trend similar complaints for the product line."
        )

    state["capa_recommendation"] = capa
    return state


# ---------------------------------------------------------------------------
# 7. Complaint Summary (bonus feature)
# ---------------------------------------------------------------------------
def summarize(state: ComplaintAgentState) -> ComplaintAgentState:
    fields = state["extracted_fields"]
    summary = None
    if _llm_configured():
        try:
            llm = get_primary_llm()
            prompt = (
                "Write a concise 2-3 sentence executive summary of this pharmaceutical customer complaint, "
                "suitable for a QMS dashboard. Return ONLY JSON: {\"summary\": \"<text>\"}\n\n"
                f"Product: {fields.get('product_name')}\nBatch: {fields.get('batch_number')}\n"
                f"Type: {fields.get('complaint_type')}\nSeverity: {fields.get('severity')}\n"
                f"Description: {fields.get('description')}\n"
                f"Risk level: {state.get('risk_level')}\nRoot cause: {state.get('root_cause_suggestion')}"
            )
            resp = llm.invoke([SystemMessage(content="Respond with strict JSON only."),
                                HumanMessage(content=prompt)])
            summary = extract_json(resp.content).get("summary")
        except Exception as e:
            state.setdefault("errors", []).append(f"summarize LLM fallback: {e}")

    if not summary:
        summary = (
            f"{fields.get('complaint_type', 'Complaint')} reported for {fields.get('product_name', 'product')} "
            f"(batch {fields.get('batch_number', 'N/A')}) with {fields.get('severity', 'Minor').lower()} "
            f"severity. Assessed risk level: {state.get('risk_level', 'Medium')}. "
            f"Suggested root cause: {state.get('root_cause_suggestion', 'under investigation')[:150]}"
        )

    state["summary"] = summary
    return state
