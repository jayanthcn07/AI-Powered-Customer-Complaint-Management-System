import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const api = axios.create({ baseURL });

// --- Complaints ------------------------------------------------------
export const listComplaints = (params = {}) =>
  api.get("/api/complaints", { params }).then((r) => r.data);

export const getComplaint = (id) =>
  api.get(`/api/complaints/${id}`).then((r) => r.data);

export const createComplaint = (payload) =>
  api.post("/api/complaints", payload).then((r) => r.data);

export const updateComplaint = (id, payload) =>
  api.patch(`/api/complaints/${id}`, payload).then((r) => r.data);

export const deleteComplaint = (id) =>
  api.delete(`/api/complaints/${id}`).then((r) => r.data);

export const getStats = () =>
  api.get("/api/complaints/stats/summary").then((r) => r.data);

export const addCapa = (complaintId, payload) =>
  api.post(`/api/complaints/${complaintId}/capa`, payload).then((r) => r.data);

// --- AI Copilot --------------------------------------------------------
export const analyzeText = (text) =>
  api.post("/api/ai/analyze", { text }).then((r) => r.data);

export const analyzeUpload = (file) => {
  const form = new FormData();
  form.append("file", file);
  return api
    .post("/api/ai/analyze-upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    .then((r) => r.data);
};

export const analyzeAndLog = (text) =>
  api.post("/api/ai/analyze-and-log", { text }).then((r) => r.data);

export const reanalyzeComplaint = (id) =>
  api.post(`/api/ai/reanalyze/${id}`).then((r) => r.data);

export const getHealth = () => api.get("/api/health").then((r) => r.data);
