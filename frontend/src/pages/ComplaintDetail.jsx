import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, RefreshCw } from "lucide-react";
import { fetchComplaint, clearSelected, updateComplaintThunk, reanalyzeComplaintThunk } from "../store/complaintsSlice";
import AICopilotPanel from "../components/AICopilotPanel";
import { RiskBadge, SeverityBadge, StatusBadge } from "../components/Badges";
import "./ComplaintDetail.css";

export default function ComplaintDetail() {
  const { id } = useParams();
  const dispatch = useDispatch();
  const { selected: c, status } = useSelector((s) => s.complaints);
  const [reanalyzing, setReanalyzing] = useState(false);

  useEffect(() => {
    dispatch(fetchComplaint(id));
    return () => dispatch(clearSelected());
  }, [dispatch, id]);

  if (!c) {
    return <div className="detail-page"><p className="table-empty">Loading complaint...</p></div>;
  }

  const aiResult = c.ai_analysis_complete
    ? {
        extracted_fields: c.ai_extracted_fields,
        summary: c.ai_summary,
        completeness_score: c.ai_completeness_score,
        missing_fields: c.ai_missing_fields,
        risk_level: c.ai_risk_level,
        risk_score: c.ai_risk_score,
        risk_rationale: c.ai_risk_rationale,
        root_cause_suggestion: c.ai_root_cause_suggestion,
        capa_recommendation: c.ai_capa_recommendation,
        is_duplicate: c.ai_is_duplicate,
        duplicate_of: c.ai_duplicate_of,
        duplicate_rationale: c.ai_duplicate_rationale,
      }
    : null;

  const handleStatusChange = (e) => {
    dispatch(updateComplaintThunk({ id: c.id, payload: { status: e.target.value } }));
  };

  const handleReanalyze = async () => {
    setReanalyzing(true);
    try {
      await dispatch(reanalyzeComplaintThunk(c.id)).unwrap();
    } finally {
      setReanalyzing(false);
    }
  };

  return (
    <div className="detail-page">
      <Link to="/" className="back-link"><ArrowLeft size={14} /> Back to dashboard</Link>

      <div className="detail-header">
        <div>
          <span className="eyebrow">{c.complaint_number}</span>
          <h1>{c.product_name}</h1>
          <div className="detail-badges">
            <SeverityBadge severity={c.severity} />
            <RiskBadge level={c.ai_risk_level} />
            <StatusBadge status={c.status} />
          </div>
        </div>
        <div className="detail-actions">
          <select value={c.status} onChange={handleStatusChange} className="status-select">
            <option>New</option>
            <option>Under Investigation</option>
            <option>CAPA Initiated</option>
            <option>Closed</option>
          </select>
          <button className="btn btn-ghost" onClick={handleReanalyze} disabled={reanalyzing}>
            <RefreshCw size={14} className={reanalyzing ? "spin" : ""} /> Re-run AI Copilot
          </button>
        </div>
      </div>

      <div className="detail-layout">
        <div className="detail-main">
          <section className="card">
            <h3 className="card-title">Customer</h3>
            <div className="kv-grid">
              <KV label="Name" value={c.customer_name} />
              <KV label="Email" value={c.customer_email} />
              <KV label="Contact" value={c.customer_contact} />
              <KV label="Source channel" value={c.source_channel} />
            </div>
          </section>

          <section className="card">
            <h3 className="card-title">Product & batch</h3>
            <div className="kv-grid">
              <KV label="Product" value={c.product_name} />
              <KV label="Product code" value={c.product_code} />
              <KV label="Batch number" value={c.batch_number} />
              <KV label="Market" value={c.market} />
              <KV label="Manufacturing date" value={c.manufacturing_date} />
              <KV label="Expiry date" value={c.expiry_date} />
            </div>
          </section>

          <section className="card">
            <h3 className="card-title">Complaint description</h3>
            <p className="description-text">{c.description}</p>
          </section>

          {c.raw_source_text && (
            <section className="card">
              <h3 className="card-title">Original source text</h3>
              <p className="description-text raw-text">{c.raw_source_text}</p>
            </section>
          )}
        </div>

        <div className="detail-side">
          <AICopilotPanel result={aiResult} loading={reanalyzing} error={null} />
        </div>
      </div>
    </div>
  );
}

function KV({ label, value }) {
  return (
    <div className="kv">
      <span className="kv-label">{label}</span>
      <span className="kv-value">{value || "—"}</span>
    </div>
  );
}

