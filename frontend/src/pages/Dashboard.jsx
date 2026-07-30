import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Link } from "react-router-dom";
import { AlertTriangle, FolderOpen, Copy, ListChecks, Search, Plus } from "lucide-react";
import { fetchComplaints, fetchStats, setFilters } from "../store/complaintsSlice";
import { RiskBadge, SeverityBadge, StatusBadge } from "../components/Badges";
import "./Dashboard.css";

export default function Dashboard() {
  const dispatch = useDispatch();
  const { items, stats, status, filters } = useSelector((s) => s.complaints);

  useEffect(() => {
    dispatch(fetchStats());
  }, [dispatch]);

  useEffect(() => {
    const params = {};
    if (filters.status) params.status = filters.status;
    if (filters.severity) params.severity = filters.severity;
    if (filters.risk_level) params.risk_level = filters.risk_level;
    if (filters.search) params.search = filters.search;
    dispatch(fetchComplaints(params));
  }, [dispatch, filters]);

  return (
    <div className="dash-page">
      <div className="dash-header">
        <div>
          <span className="eyebrow">Overview</span>
          <h1>Complaint Dashboard</h1>
        </div>
        <Link to="/log" className="btn btn-primary">
          <Plus size={15} /> Log Customer Complaint
        </Link>
      </div>

      <div className="stat-grid">
        <StatCard icon={<ListChecks size={17} />} label="Total complaints" value={stats?.total_complaints ?? "-"} />
        <StatCard icon={<AlertTriangle size={17} />} label="High risk" value={stats?.high_risk ?? "-"} tone="high" />
        <StatCard icon={<FolderOpen size={17} />} label="Open" value={stats?.open_complaints ?? "-"} />
        <StatCard icon={<Copy size={17} />} label="Flagged duplicates" value={stats?.duplicate_complaints ?? "-"} />
      </div>

      <div className="card">
        <div className="filters-row">
          <div className="search-box">
            <Search size={14} />
            <input
              placeholder="Search customer, product, complaint #..."
              value={filters.search}
              onChange={(e) => dispatch(setFilters({ search: e.target.value }))}
            />
          </div>
          <select value={filters.status} onChange={(e) => dispatch(setFilters({ status: e.target.value }))}>
            <option value="">All statuses</option>
            <option>New</option>
            <option>Under Investigation</option>
            <option>CAPA Initiated</option>
            <option>Closed</option>
          </select>
          <select value={filters.severity} onChange={(e) => dispatch(setFilters({ severity: e.target.value }))}>
            <option value="">All severities</option>
            <option>Critical</option>
            <option>Major</option>
            <option>Minor</option>
          </select>
          <select value={filters.risk_level} onChange={(e) => dispatch(setFilters({ risk_level: e.target.value }))}>
            <option value="">All AI risk levels</option>
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>
        </div>

        <div className="table-wrap">
          <table className="complaints-table">
            <thead>
              <tr>
                <th>Complaint #</th>
                <th>Customer</th>
                <th>Product / Batch</th>
                <th>Type</th>
                <th>Severity</th>
                <th>AI Risk</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {status === "loading" && (
                <tr><td colSpan={7} className="table-empty">Loading complaints...</td></tr>
              )}
              {status !== "loading" && items.length === 0 && (
                <tr><td colSpan={7} className="table-empty">No complaints match these filters.</td></tr>
              )}
              {items.map((c) => (
                <tr key={c.id}>
                  <td>
                    <Link className="table-link" to={`/complaints/${c.id}`}>{c.complaint_number}</Link>
                  </td>
                  <td>
                    <div className="cell-primary">{c.customer_name}</div>
                    <div className="cell-secondary">{c.customer_email || "—"}</div>
                  </td>
                  <td>
                    <div className="cell-primary">{c.product_name}</div>
                    <div className="cell-secondary">{c.batch_number || "—"}</div>
                  </td>
                  <td>{c.complaint_type}</td>
                  <td><SeverityBadge severity={c.severity} /></td>
                  <td><RiskBadge level={c.ai_risk_level} /></td>
                  <td><StatusBadge status={c.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, tone }) {
  return (
    <div className={`stat-card${tone ? ` stat-card-${tone}` : ""}`}>
      <div className="stat-icon">{icon}</div>
      <div>
        <div className="stat-value">{value}</div>
        <div className="stat-label">{label}</div>
      </div>
    </div>
  );
}
