import { useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { UploadCloud, Wand2, Save, FileText, X } from "lucide-react";
import { runAnalyzeText, runAnalyzeUpload, clearAiResult } from "../store/aiSlice";
import { createComplaintThunk, reanalyzeComplaintThunk } from "../store/complaintsSlice";
import AICopilotPanel from "../components/AICopilotPanel";
import "./LogComplaint.css";

const EMPTY_FORM = {
  customer_name: "",
  customer_email: "",
  customer_contact: "",
  product_name: "",
  product_code: "",
  batch_number: "",
  manufacturing_date: "",
  expiry_date: "",
  market: "",
  complaint_type: "Other",
  severity: "Minor",
  description: "",
  status: "New",
};

const COMPLAINT_TYPES = [
  "Quality Defect", "Adverse Event", "Packaging/Labeling",
  "Product Efficacy", "Contamination", "Delivery/Logistics", "Other",
];
const SEVERITIES = ["Minor", "Major", "Critical"];

export default function LogComplaint() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { result, status, error } = useSelector((s) => s.ai);

  const [sourceText, setSourceText] = useState("");
  const [fileName, setFileName] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => () => dispatch(clearAiResult()), [dispatch]);

  // Auto-populate the manual form whenever a fresh AI extraction arrives.
  useEffect(() => {
    if (result?.extracted_fields) {
      const f = result.extracted_fields;
      setForm((prev) => ({
        ...prev,
        customer_name: f.customer_name || prev.customer_name,
        customer_email: f.customer_email || prev.customer_email,
        customer_contact: f.customer_contact || prev.customer_contact,
        product_name: f.product_name || prev.product_name,
        product_code: f.product_code || prev.product_code,
        batch_number: f.batch_number || prev.batch_number,
        manufacturing_date: f.manufacturing_date || prev.manufacturing_date,
        expiry_date: f.expiry_date || prev.expiry_date,
        market: f.market || prev.market,
        complaint_type: COMPLAINT_TYPES.includes(f.complaint_type) ? f.complaint_type : prev.complaint_type,
        severity: SEVERITIES.includes(f.severity) ? f.severity : prev.severity,
        description: f.description || prev.description,
      }));
    }
  }, [result]);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    dispatch(runAnalyzeUpload(file));
  };

  const handleRunAiFromText = () => {
    if (!sourceText.trim()) return;
    setFileName(null);
    dispatch(runAnalyzeText(sourceText));
  };

  const clearSource = () => {
    setSourceText("");
    setFileName(null);
    dispatch(clearAiResult());
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleFieldChange = (field) => (e) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = { ...form, raw_source_text: sourceText || null, attachment_filename: fileName };
      const created = await dispatch(createComplaintThunk(payload)).unwrap();
      // Ensure the saved record carries a full AI Copilot risk assessment,
      // consistent with whatever text/fields were ultimately submitted.
      await dispatch(reanalyzeComplaintThunk(created.id)).unwrap();
      navigate(`/complaints/${created.id}`);
    } catch (err) {
      console.error(err);
      alert("Failed to save complaint. Check that the backend is running.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="log-page">
      <div className="log-page-header">
        <div>
          <span className="eyebrow">New record</span>
          <h1>Log Customer Complaint</h1>
          <p className="log-page-desc">
            Paste an email or upload a complaint document, then run the AI Copilot to
            auto-fill the form below - or enter details manually.
          </p>
        </div>
      </div>

      <div className="log-layout">
        <div className="log-main">
          <section className="card">
            <h3 className="card-title">1. Complaint source</h3>
            <textarea
              className="source-textarea"
              placeholder="Paste a customer email or complaint text here..."
              value={sourceText}
              onChange={(e) => setSourceText(e.target.value)}
              rows={7}
            />
            <div className="source-actions">
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleRunAiFromText}
                disabled={status === "loading" || !sourceText.trim()}
              >
                <Wand2 size={15} /> Run AI Copilot
              </button>

              <label className="btn btn-ghost upload-btn">
                <UploadCloud size={15} /> Upload PDF / TXT
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.txt"
                  hidden
                  onChange={handleFileChange}
                />
              </label>

              {(sourceText || fileName) && (
                <button type="button" className="btn btn-plain" onClick={clearSource}>
                  <X size={14} /> Clear
                </button>
              )}
            </div>
            {fileName && (
              <div className="file-chip">
                <FileText size={13} /> {fileName}
              </div>
            )}
          </section>

          <form className="card" onSubmit={handleSubmit}>
            <h3 className="card-title">2. Complaint details</h3>
            <div className="form-grid">
              <Field label="Customer name *">
                <input required value={form.customer_name} onChange={handleFieldChange("customer_name")} />
              </Field>
              <Field label="Customer email">
                <input type="email" value={form.customer_email} onChange={handleFieldChange("customer_email")} />
              </Field>
              <Field label="Customer contact">
                <input value={form.customer_contact} onChange={handleFieldChange("customer_contact")} />
              </Field>
              <Field label="Market">
                <input value={form.market} onChange={handleFieldChange("market")} />
              </Field>

              <Field label="Product name *">
                <input required value={form.product_name} onChange={handleFieldChange("product_name")} />
              </Field>
              <Field label="Product code">
                <input value={form.product_code} onChange={handleFieldChange("product_code")} />
              </Field>
              <Field label="Batch number">
                <input value={form.batch_number} onChange={handleFieldChange("batch_number")} />
              </Field>
              <Field label="Manufacturing date">
                <input placeholder="YYYY-MM-DD" value={form.manufacturing_date} onChange={handleFieldChange("manufacturing_date")} />
              </Field>
              <Field label="Expiry date">
                <input placeholder="YYYY-MM-DD" value={form.expiry_date} onChange={handleFieldChange("expiry_date")} />
              </Field>

              <Field label="Complaint type">
                <select value={form.complaint_type} onChange={handleFieldChange("complaint_type")}>
                  {COMPLAINT_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                </select>
              </Field>
              <Field label="Severity">
                <select value={form.severity} onChange={handleFieldChange("severity")}>
                  {SEVERITIES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </Field>

              <Field label="Description" full>
                <textarea
                  required
                  rows={4}
                  value={form.description}
                  onChange={handleFieldChange("description")}
                />
              </Field>
            </div>

            <div className="form-footer">
              <button type="submit" className="btn btn-primary" disabled={saving}>
                <Save size={15} /> {saving ? "Saving..." : "Log Complaint"}
              </button>
            </div>
          </form>
        </div>

        <div className="log-side">
          <AICopilotPanel result={result} loading={status === "loading"} error={error} />
        </div>
      </div>
    </div>
  );
}

function Field({ label, children, full }) {
  return (
    <label className={`field${full ? " field-full" : ""}`}>
      <span className="field-label">{label}</span>
      {children}
    </label>
  );
}
