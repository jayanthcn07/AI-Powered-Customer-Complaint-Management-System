import { ShieldAlert, Gauge, Microscope, ClipboardList, Copy, CheckCircle2, Sparkles } from "lucide-react";
import { RiskBadge } from "./Badges";
import "./AICopilotPanel.css";

const STAGES = [
  "Extract", "Completeness", "Duplicate check", "Risk", "Root cause", "CAPA", "Summary",
];

export default function AICopilotPanel({ result, loading, error }) {
  return (
    <div className="copilot-panel">
      <div className="copilot-header">
        <div className="copilot-title">
          <Sparkles size={16} strokeWidth={2} />
          <h3>AI Copilot Risk Assessment</h3>
        </div>
        <span className="copilot-sub">LangGraph workflow &middot; Groq (gemma2-9b-it / llama-3.3-70b)</span>
      </div>

      <div className="copilot-stepper">
        {STAGES.map((stage, i) => (
          <div key={stage} className={`copilot-step ${result ? "done" : loading ? "active" : ""}`}>
            <div className="copilot-step-dot">{result ? <CheckCircle2 size={13} /> : i + 1}</div>
            <span>{stage}</span>
          </div>
        ))}
      </div>

      {loading && (
        <div className="copilot-empty">
          <div className="copilot-spinner" />
          Running extraction, risk classification, root cause and CAPA nodes&hellip;
        </div>
      )}

      {error && !loading && <div className="copilot-error">{error}</div>}

      {!result && !loading && !error && (
        <div className="copilot-empty">
          Paste a complaint email, upload a document, or fill the form and run the
          AI Copilot to see the extracted fields, risk assessment, root cause and CAPA
          recommendation here.
        </div>
      )}

      {result && (
        <div className="copilot-body">
          <div className="copilot-risk-row">
            <div className="copilot-risk-score">
              <Gauge size={18} strokeWidth={1.8} />
              <div>
                <div className="copilot-risk-score-value">{Math.round(result.risk_score ?? 0)}</div>
                <div className="copilot-risk-score-label">Risk score / 100</div>
              </div>
            </div>
            <RiskBadge level={result.risk_level} />
            {result.is_duplicate && (
              <span className="badge badge-risk-medium">
                <Copy size={11} /> Possible duplicate
              </span>
            )}
          </div>

          {result.risk_rationale && (
            <p className="copilot-rationale">
              <ShieldAlert size={13} style={{ marginRight: 5, verticalAlign: -2 }} />
              {result.risk_rationale}
            </p>
          )}

          <div className="copilot-section">
            <div className="copilot-section-title">Completeness</div>
            <div className="copilot-completeness">
              <div className="copilot-progress-track">
                <div
                  className="copilot-progress-fill"
                  style={{ width: `${result.completeness_score ?? 0}%` }}
                />
              </div>
              <span>{result.completeness_score ?? 0}%</span>
            </div>
            {result.missing_fields?.length > 0 && (
              <p className="copilot-missing">
                Missing: {result.missing_fields.join(", ")}
              </p>
            )}
          </div>

          {result.summary && (
            <div className="copilot-section">
              <div className="copilot-section-title">Summary</div>
              <p className="copilot-text">{result.summary}</p>
            </div>
          )}

          {result.root_cause_suggestion && (
            <div className="copilot-section">
              <div className="copilot-section-title">
                <Microscope size={13} /> Root cause suggestion
              </div>
              <p className="copilot-text">{result.root_cause_suggestion}</p>
            </div>
          )}

          {result.capa_recommendation && (
            <div className="copilot-section">
              <div className="copilot-section-title">
                <ClipboardList size={13} /> CAPA recommendation
              </div>
              <p className="copilot-text copilot-pre">{result.capa_recommendation}</p>
            </div>
          )}

          {result.is_duplicate && result.duplicate_rationale && (
            <div className="copilot-section">
              <div className="copilot-section-title">Duplicate check</div>
              <p className="copilot-text">{result.duplicate_rationale}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
