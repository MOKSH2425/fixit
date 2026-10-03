# FixIt

> **See a problem. Get an action.**

FixIt is a multimodal AI action agent that accepts visual inputs—such as software error screenshots, college notices, assignment instructions, and technical warnings—and translates them directly into structured remediation plans, actionable verification checklists, and persistent application tasks.

Built for **MLH Hacktoberfest Hack Day Surat 2026** competing in:
- **Best Use of Gemma 4**
- **Best Open-Source AI Project**

---

## 1. Problem Statement

People frequently receive critical information visually:
- Software error stack traces
- Academic and university circulars
- Assignment sheets and project rubrics
- Configuration warnings and terminal failures

Existing AI tools often stop at descriptive image captioning: *"This image shows a Python terminal error with ModuleNotFoundError."* While that explains the image, it does not move the user forward. The user still has to ask:
- *What is the actual underlying problem?*
- *What should I do first?*
- *What are the exact steps to resolve it?*
- *What deadlines or checklist items must I track?*

## 2. Solution: The Multimodal Action Loop

FixIt bridges the gap between **visual understanding** and **real action**:

```
SEE ──► UNDERSTAND ──► DECIDE ──► ACT
```

1. **SEE**: User uploads an image (or uses one-click demo presets) with an optional prompt.
2. **UNDERSTAND**: Gemma 4 multimodal model parses visual hierarchy, text, error signatures, and dates.
3. **DECIDE**: The agent selects which registered backend tools to call.
4. **ACT**: The backend executes the tools, validates arguments, updates SQLite database state, and delivers structured next steps.

---

## 3. Why Multimodal & Why Gemma 4?

- **Native Multimodal Understanding**: Gemma 4 natively reasons across pixels and text tokens without relying on brittle external OCR pipelines.
- **Agentic Decision Layer**: Rather than generating decorative text, Gemma 4 decides which tools to call and structures the parameters.
- **Architectural Principle**: **The model decides. The backend executes.** Gemma 4 never executes arbitrary shell, python, or SQL code directly. The backend validates every tool request within a safe execution sandbox.

---

## 4. Architecture

```text
Browser (React + Vite)
       │
       │ multipart/form-data
       ▼
FastAPI Application Backend (Port 8000)
       │
       ├────────────────────────────────────────┐
       ▼                                        ▼
Gemma 4 Multimodal Agent                    SQLite Database
(via Google GenAI SDK)                      (data/fixit.db)
       │
       │ Function Calls
       ▼
Tool Registry
       ├── analyze_image
       ├── generate_action_plan
       ├── generate_checklist
       └── create_task
```

### Registered Tools
1. **`analyze_image`**: Extracts structured problem classification, root cause, key details, and confidence assessment.
2. **`generate_action_plan`**: Formulates 3–6 ordered, concrete remediation steps grounded in evidence.
3. **`generate_checklist`**: Generates interactive checklist items corresponding to the action plan.
4. **`create_task`**: Persists actionable items into SQLite with title, category, and deadline.

---

## 5. Project Structure

```text
FIXIT/
├── backend/
│   ├── ai/
│   │   ├── __init__.py
│   │   └── model_client.py     # Google GenAI Gemma 4 client & tool schemas
│   ├── tools/
│   │   ├── __init__.py         # Tool registry (TOOLS dict)
│   │   ├── analyze_image.py    # Image diagnosis tool
│   │   ├── action_plan.py      # Action plan generation tool
│   │   ├── checklist.py        # Checklist generation tool
│   │   └── task_creator.py     # SQLite task creation tool
│   ├── agent.py                # Agent orchestration loop
│   ├── config.py               # Environment configuration
│   ├── database.py             # SQLite connection & CRUD functions
│   ├── main.py                 # FastAPI server & REST endpoints
│   ├── schemas.py              # Pydantic data models
│   ├── test_backend.py         # Pytest API integration tests
│   ├── test_tools.py           # Pytest tool unit tests
│   ├── create_demo_fixtures.py # Demo screenshot & notice generator
│   ├── requirements.txt        # Python backend dependencies
│   ├── .env.example            # Environment variables template
│   └── .env                    # Local environment secrets (not committed)
│
├── frontend/
│   ├── public/
│   │   └── demo/               # Bundled sample screenshots & notices
│   ├── src/
│   │   ├── components/
│   │   │   ├── ImageUploader.jsx
│   │   │   ├── ImagePreview.jsx
│   │   │   ├── AgentActivity.jsx
│   │   │   ├── ProblemCard.jsx
│   │   │   ├── ActionPlan.jsx
│   │   │   ├── Checklist.jsx
│   │   │   ├── TaskCard.jsx
│   │   │   └── TaskList.jsx
│   │   ├── services/
│   │   │   └── api.js          # Centralized API service
│   │   ├── App.jsx             # Main dashboard
│   │   ├── main.jsx            # React root mount
│   │   └── index.css           # Slate & indigo design system
│   ├── package.json
│   └── vite.config.js
│
├── demo/
│   ├── technical_error.png     # ModuleNotFoundError: No module named 'fastapi'
│   └── sample_notice.png       # Semester 6 Project Report submission notice
│
├── data/
│   └── fixit.db                # SQLite database (auto-created on startup)
│
├── FixIt_PRD.md                # Product Requirements Document
├── FixIt_TRD.md                # Technical Requirements Document
├── LICENSE                     # MIT Open Source License
├── README.md                   # This documentation
└── .gitignore
```

---

## 6. Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- A Google Gemini / Gemma API Key (get one from [Google AI Studio](https://aistudio.google.com/))

### 1. Clone & Configure Backend
```bash
git clone https://github.com/your-username/fixit.git
cd fixit/backend

# Create virtual environment (optional but recommended)
python -m venv venv
# On Windows: venv\Scripts\activate
# On Linux/macOS: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env from template
copy .env.example .env
```

Edit `backend/.env` with your API credentials:
```env
GEMINI_API_KEY=your_actual_api_key_here
GEMMA_MODEL=gemma-4-26b-a4b-it
HOST=127.0.0.1
PORT=8000
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DATABASE_URL=../data/fixit.db
```

### 2. Configure Frontend
```bash
cd ../frontend
npm install
```

---

## 7. Running the Application

### Start Backend
In terminal 1:
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```
Backend runs at: `http://127.0.0.1:8000`  
Interactive Swagger Docs: `http://127.0.0.1:8000/docs`

### Start Frontend
In terminal 2:
```bash
cd frontend
npm run dev
```
Frontend runs at: `http://127.0.0.1:5173`

---

## 8. Two-Minute Live Demonstration Flow

The repository comes pre-bundled with demo fixtures to execute a live demonstration in under 2 minutes:

### Demo 1: Technical Error Diagnosis
1. Open `http://localhost:5173`.
2. Click **⚡ Demo 1: Error Screenshot** (or upload `demo/technical_error.png`).
3. Click **Analyze & Generate Action**.
4. Observe **Gemma 4 Multimodal Agent Execution**:
   - `✓ Image understood`
   - `✓ Problem identified`
   - `✓ Action plan generated`
   - `✓ Checklist generated`
5. Inspect the output:
   - **Problem Detected**: Missing Python dependency (`ModuleNotFoundError: No module named 'fastapi'`).
   - **Action Plan**:
     1. Install FastAPI in active environment.
     2. Verify active environment.
     3. Run application again.
   - **Verification Checklist**: Interactive checkboxes.

### Demo 2: College Notice to Persistent SQLite Tasks
1. Click **📋 Demo 2: College Notice** (or upload `demo/sample_notice.png`).
2. Click **Analyze & Generate Action**.
3. FixIt extracts the deadline (**October 8, 2026**) and required student actions.
4. Click **Create Tasks in Application**.
5. Observe: `✓ 3 tasks created` and tasks instantly appear in **Persistent Application Tasks**.
6. Toggle task completion checkboxes.
7. **Refresh the browser**: The tasks remain intact from the SQLite database.

---

## 9. Running Tests

Run the backend test suite:
```bash
# Test API endpoints, validation, and database CRUD
python -m pytest backend/test_backend.py -v

# Test each of the 4 FixIt tools independently
python -m pytest backend/test_tools.py -v
```

---

## 10. Security & Safety Principles

1. **No Arbitrary Execution**: FixIt will never execute shell commands, arbitrary Python code, or raw SQL queries suggested by language models.
2. **Frontend Protection**: The Gemini API key is strictly isolated on the FastAPI server and is never transmitted to or bundled with the client application.
3. **Model Grounding**: Actions and checklists are restricted to verifiable visual evidence.

---

## 11. Future Scope

- Support for multi-page PDF documents and scanned hand-written notices.
- Native calendar sync (iCal / Google Calendar) for extracted academic deadlines.
- Browser-assisted automated remediation workflows requiring explicit human confirmation.

---

## 12. License

This project is licensed under the [MIT License](LICENSE).
