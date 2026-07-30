import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import LogComplaint from "./pages/LogComplaint";
import ComplaintDetail from "./pages/ComplaintDetail";

export default function App() {
  return (
    <div className="app-shell">
      <Sidebar />
      <main>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/log" element={<LogComplaint />} />
          <Route path="/complaints/:id" element={<ComplaintDetail />} />
        </Routes>
      </main>
    </div>
  );
}
