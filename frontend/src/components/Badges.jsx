import "./Badges.css";

export function RiskBadge({ level }) {
  if (!level) return <span className="badge badge-neutral">Not assessed</span>;
  const cls = { High: "badge-risk-high", Medium: "badge-risk-medium", Low: "badge-risk-low" }[level] || "badge-neutral";
  return <span className={`badge ${cls}`}>{level} risk</span>;
}

export function SeverityBadge({ severity }) {
  const cls = {
    Critical: "badge-risk-high",
    Major: "badge-risk-medium",
    Minor: "badge-neutral-outline",
  }[severity] || "badge-neutral-outline";
  return <span className={`badge ${cls}`}>{severity}</span>;
}

export function StatusBadge({ status }) {
  const cls = {
    New: "badge-status-new",
    "Under Investigation": "badge-status-progress",
    "CAPA Initiated": "badge-status-progress",
    Closed: "badge-status-closed",
  }[status] || "badge-neutral";
  return <span className={`badge ${cls}`}>{status}</span>;
}
