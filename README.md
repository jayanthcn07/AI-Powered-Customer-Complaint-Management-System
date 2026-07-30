# AI-Powered Customer Complaint Management System

An AI-driven Customer Complaint Management module for pharmaceutical Quality Management Systems (QMS) supporting both **API (Active Pharmaceutical Ingredient)** and **FDF (Finished Dosage Form)** manufacturing workflows.

This project was developed as part of the **AIVOA.AI Round 1 – AI Product Engineer Assignment**.

The system leverages an AI Copilot powered by **LangGraph** and **Groq LLMs** to automate complaint analysis. Users can paste a customer complaint email or upload a complaint document, and the application extracts structured information, evaluates complaint quality, identifies potential duplicates, performs risk assessment, recommends probable root causes and CAPA actions, and generates an executive summary.

The extracted insights automatically populate the **Log Customer Complaint** form and the **AI Copilot Risk Assessment** dashboard, significantly reducing manual effort and improving consistency.

---

## ✨ Features

- 📧 Parse complaint emails or uploaded documents
- 🤖 AI-powered structured data extraction
- ✅ Complaint completeness validation
- 🔍 Duplicate complaint detection
- ⚠️ Automated risk classification with rationale
- 🧩 Root cause recommendations
- 🛠️ Corrective and Preventive Action (CAPA) suggestions
- 📝 Executive complaint summary
- 📋 Automatic form population for complaint logging

---

## 🏗️ Technology Stack

| Layer | Technology |
|--------|------------|
| Frontend | React (Vite) + Redux Toolkit |
| Backend | Python + FastAPI |
| AI Workflow | LangGraph |
| Large Language Models | Groq (`gemma2-9b-it` for primary processing, `llama-3.3-70b-versatile` for Root Cause Analysis & CAPA recommendations) |
| Database | SQLite (default), MySQL, PostgreSQL via `DATABASE_URL` |
| ORM | SQLAlchemy |
| UI Font | Google Inter |

---

## 📁 Project Structure

```text
.
├── backend/      # FastAPI backend, LangGraph workflow, SQLAlchemy models
│                 # See backend/README.md
│
├── frontend/     # React (Vite) application with Redux Toolkit
│                 # See frontend/README.md
│
└── README.md
```

---

## 🤖 AI Copilot Workflow

The application uses a **LangGraph** workflow to orchestrate multiple AI reasoning steps.

```text
Extract Information
        │
        ▼
Completeness Check
        │
        ▼
Duplicate Detection
        │
        ▼
Risk Classification
        │
        ▼
Root Cause Recommendation
        │
        ▼
CAPA Recommendation
        │
        ▼
Complaint Summary
```

---

## 🧠 AI Workflow Components

| Stage | Description |
|--------|-------------|
| **Information Extraction** | Extracts structured complaint details such as customer, product, batch number, complaint type, severity, incident date, and description from unstructured text or uploaded documents. |
| **Completeness Validation** | Verifies the presence of required QMS fields, calculates a completeness score, and identifies missing information. |
| **Duplicate Detection** | Detects potential duplicate complaints by comparing product, batch, and issue similarity with previously logged complaints. |
| **Risk Classification** | Assigns a **High**, **Medium**, or **Low** risk level along with a confidence score and explanation. |
| **Root Cause Recommendation** | Suggests the most probable root cause category using advanced reasoning powered by the `llama-3.3-70b-versatile` model. |
| **CAPA Recommendation** | Recommends appropriate Corrective and Preventive Actions (CAPA) based on the complaint context and inferred root cause. |
| **Complaint Summary** | Generates a concise executive summary suitable for dashboards and quality review. |

---

## 🚀 Workflow Overview

1. User submits a complaint via email text or document upload.
2. The AI Copilot extracts structured complaint information.
3. Required fields are validated for completeness.
4. Similar complaints are identified to detect duplicates.
5. Risk is classified based on complaint severity and context.
6. AI recommends the most likely root cause.
7. CAPA recommendations are generated.
8. An executive summary is produced.
9. The application automatically populates the complaint logging form and AI Risk Assessment panel.

---

## 🎯 Assignment Objective

This project demonstrates how AI agents can streamline pharmaceutical complaint management by automating traditionally manual QMS processes, improving data quality, accelerating investigations, and assisting quality assurance teams with intelligent decision support.