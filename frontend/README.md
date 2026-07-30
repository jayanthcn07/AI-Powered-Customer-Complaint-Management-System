# Frontend - AI-Powered Customer Complaint Management System

React (Vite) + Redux Toolkit UI. See the root `README.md` for the full
project overview - this file covers frontend specifics only.

## Local setup

```bash
cd frontend
npm install
cp .env.example .env
# VITE_API_BASE_URL should point at the backend, e.g. http://localhost:8000
npm run dev
```

App runs at http://localhost:5173

## Build for production

```bash
npm run build      # outputs static files to dist/
npm run preview    # serve the production build locally
```

## Project layout

```
src/
  api/client.js            Axios client + typed API call helpers
  store/
    store.js                Redux store
    complaintsSlice.js      Complaints CRUD + filters state
    aiSlice.js               AI Copilot (LangGraph) call state
  components/
    Sidebar.jsx              App navigation
    Badges.jsx               Risk / severity / status pill components
    AICopilotPanel.jsx       AI Copilot Risk Assessment side panel
  pages/
    Dashboard.jsx            Stats + filterable complaint table
    LogComplaint.jsx         Paste/upload -> AI Copilot -> form -> save
    ComplaintDetail.jsx      Full record + AI Copilot results + re-run
```
