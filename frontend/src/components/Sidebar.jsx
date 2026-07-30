import { NavLink } from "react-router-dom";
import { LayoutGrid, FileEdit, FlaskConical } from "lucide-react";
import "./Sidebar.css";

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-mark">Æ</div>
        <div>
          <div className="sidebar-brand-name">AIVOA QMS</div>
          <div className="sidebar-brand-sub">Complaint Management</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <NavLink to="/" end className={({ isActive }) => `sidebar-link${isActive ? " active" : ""}`}>
          <LayoutGrid size={17} strokeWidth={1.8} />
          Dashboard
        </NavLink>
        <NavLink to="/log" className={({ isActive }) => `sidebar-link${isActive ? " active" : ""}`}>
          <FileEdit size={17} strokeWidth={1.8} />
          Log Customer Complaint
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        <FlaskConical size={15} strokeWidth={1.8} />
        <span>Pharmaceutical Manufacturing &middot; API / FDF</span>
      </div>
    </aside>
  );
}
