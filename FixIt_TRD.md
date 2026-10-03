# FIXIT — Technical Requirements Document (TRD)

**Version:** 1.0  
**Date:** 03 October 2026  
**Project:** FixIt  
**Purpose:** Hackathon MVP implementation specification

---

# 1. Technical Objective

Build a local, hackathon-ready web application that:

1. accepts an image and optional text;
2. sends multimodal input to Gemma 4 through the Google AI API;
3. allows the model to request registered application tools;
4. validates and executes those tools in FastAPI;
5. persists tasks in SQLite;
6. returns structured results;
7. displays agent activity and results in React.

Core architecture:

```text
Browser
   |
   v
React + Vite
   |
   | multipart/form-data
   v
FastAPI
   |
   +--------------------+
   |                    |
   v                    v
Gemma 4 Agent       SQLite
   |
   | function calls
   v
Tool Registry
   |
   +-- analyze_image
   +-- generate_action_plan
   +-- generate_checklist
   +-- create_task
```

---

# 2. Technology Stack

## Frontend

- React
- Vite
- JavaScript
- CSS

## Backend

- Python
- FastAPI
- Pydantic
- SQLite
- Uvicorn

## AI

- Google GenAI Python SDK
- Gemma 4 through the Gemini API
- current supported API/model configuration verified at implementation time

The official Gemini API documentation currently lists Gemma 4 model IDs including:

- `gemma-4-26b-a4b-it`
- `gemma-4-31b-it`

and the current Interactions API supports agent interactions with these models. Verify live availability/access before final implementation. 

---

# 3. API Strategy

Prefer the current Google GenAI SDK and Interactions API where appropriate.

The AI layer must be isolated.

Example dependency:

```text
google-genai
```

Do not spread Google API-specific code across the application.

---

# 4. Environment Configuration

Create:

```text
backend/.env
backend/.env.example
```

Example:

```env
GEMINI_API_KEY=
GEMMA_MODEL=gemma-4-26b-a4b-it
```

The exact model should be confirmed against current account/API availability.

Never commit `.env`.

---

# 5. Project Structure

```text
fixit/
│
├── frontend/
│   ├── public/
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
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── agent.py
│   ├── ai/
│   │   ├── __init__.py
│   │   └── model_client.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── analyze_image.py
│   │   ├── action_plan.py
│   │   ├── checklist.py
│   │   └── task_creator.py
│   ├── requirements.txt
│   └── .env.example
│
├── data/
│   └── fixit.db
│
├── demo/
│   ├── technical_error.png
│   └── sample_notice.png
│
├── README.md
├── LICENSE
└── .gitignore
```

If keeping the SQLite database under `backend/` is simpler, that is acceptable; choose one location and document it.

---

# 6. Backend API

## POST /agent

Purpose:

Process an image and optional instruction.

Request:

`multipart/form-data`

Fields:

- `image`: uploaded file
- `message`: optional string

Response:

```json
{
  "success": true,
  "category": "technical_error",
  "title": "Missing Python dependency",
  "problem": "FastAPI is not installed",
  "actions": [
    "Install the missing dependency",
    "Verify the active Python environment",
    "Run the application again"
  ],
  "checklist": [
    "Install dependency",
    "Verify environment",
    "Run application"
  ],
  "created_tasks": [],
  "agent_activity": [
    "Image understood",
    "Problem identified",
    "Action plan generated",
    "Checklist generated"
  ],
  "final_response": "..."
}
```

---

## GET /tasks

Return persisted tasks.

---

## POST /tasks

Create a task.

Request:

```json
{
  "title": "Submit project report",
  "description": "Submit the final Semester 6 project report.",
  "category": "Academic",
  "deadline": "2026-10-08"
}
```

---

## PATCH /tasks/{task_id}

Update completion state and/or allowed fields.

Minimum supported operation:

```json
{
  "completed": true
}
```

---

## GET /health

Return:

```json
{
  "status": "ok"
}
```

---

# 7. Database Schema

SQLite table:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL DEFAULT 'Other',
    deadline TEXT,
    completed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
```

Use parameterized SQL or a safe SQLite abstraction.

Never concatenate model-generated strings into SQL.

---

# 8. Pydantic Schemas

Define clear schemas.

Example:

```text
TaskCreate
TaskUpdate
TaskResponse
AgentResponse
ActionPlan
ChecklistItem
ImageAnalysis
```

Use response models rather than returning arbitrary nested dictionaries from every endpoint.

---

# 9. AI Layer

File:

```text
backend/ai/model_client.py
```

Responsibilities:

- initialize `genai.Client`
- load API key
- load model
- define function declarations
- send multimodal input
- receive model response
- identify function calls
- return structured model events

The current Google documentation shows Python usage through:

```python
from google import genai
client = genai.Client()
```

and function declarations passed as tools. 

---

# 10. Function Calling Architecture

Use this exact conceptual sequence:

```text
1. User image + message
        |
        v
2. Gemma
        |
        v
3. function_call
        |
        v
4. FastAPI validates call
        |
        v
5. registered Python function executes
        |
        v
6. function_result
        |
        v
7. Gemma final response
```

The model does NOT execute Python.

Google's official function-calling documentation explicitly states that the application is responsible for executing the requested function and returning its result to the model. Multiple and compositional function calls are supported. 

---

# 11. Tool Registry

Create:

```python
TOOLS = {
    "analyze_image": analyze_image,
    "generate_action_plan": generate_action_plan,
    "generate_checklist": generate_checklist,
    "create_task": create_task,
}
```

The agent must reject unknown tool names.

---

# 12. Tool 1 — analyze_image

Purpose:

Extract actionable understanding from the visual input.

Expected result:

```json
{
  "category": "technical_error",
  "title": "Missing Python dependency",
  "problem": "The screenshot shows that the fastapi module cannot be imported.",
  "important_details": [
    "Python",
    "FastAPI",
    "ModuleNotFoundError"
  ],
  "confidence": "high"
}
```

Categories:

```text
technical_error
assignment
campus_notice
instructions
document
general_problem
unknown
```

Do not use confidence as a fake numerical scientific score. Use simple qualitative values if needed.

---

# 13. Tool 2 — generate_action_plan

Input:

- image analysis
- user message

Output:

```json
{
  "summary": "...",
  "priority": "medium",
  "actions": [
    "...",
    "...",
    "..."
  ]
}
```

Rules:

- don't invent missing facts
- keep steps concrete
- prefer 3–6 actions
- order actions logically

---

# 14. Tool 3 — generate_checklist

Input:

Action plan.

Output:

```json
{
  "items": [
    "Complete project report",
    "Print final copy",
    "Submit before deadline"
  ]
}
```

---

# 15. Tool 4 — create_task

Input:

```json
{
  "title": "...",
  "description": "...",
  "category": "Academic",
  "deadline": "YYYY-MM-DD"
}
```

Validate:

- title required
- category must be one of allowed values
- deadline must be valid or null

Allowed categories:

```text
Academic
Personal
Campus
Technical
Other
```

Insert into SQLite.

Return:

```json
{
  "success": true,
  "task_id": 1,
  "title": "...",
  "deadline": "..."
}
```

---

# 16. Agent Orchestration

File:

```text
backend/agent.py
```

Responsibilities:

1. receive uploaded image
2. validate image
3. prepare model input
4. provide registered tools
5. inspect function calls
6. execute only registered tools
7. capture tool results
8. send results back to model when needed
9. construct final application response

Do not place all logic in `main.py`.

---

# 17. Tool Selection Rules

The system prompt should tell the model:

Use `analyze_image` when visual interpretation is required.

Use `generate_action_plan` when the user needs next steps.

Use `generate_checklist` when the result can be converted into checkable actions.

Use `create_task` only when:
- the user asks to create/save a task, OR
- the user explicitly confirms creation through the UI.

For notice demo, the preferred flow is:

```text
Analyze
→ Action Plan
→ Checklist
→ user clicks Create Tasks
→ backend creates tasks
```

This avoids silently creating persistent data without clear user intent.

---

# 18. Important Agent Safety Rule

Never let model-generated text become direct executable code.

For example, if model outputs:

```text
rm -rf ...
```

the application must NOT execute it.

Commands may be displayed as recommendations when appropriate, but no arbitrary shell tool is exposed in the MVP.

---

# 19. Image Handling

FastAPI receives the image.

Validate:

- MIME type
- file size
- readable content

Do not permanently store uploaded images unless required.

For MVP:

```text
Upload
→ read bytes
→ send to model
→ process
→ discard temporary upload
```

Demo images may live in `/demo`.

---

# 20. CORS

Allow the local Vite frontend to call FastAPI.

During development, configure a limited local origin such as:

```text
http://localhost:5173
```

Do not use unrestricted CORS unless necessary.

---

# 21. Frontend API Service

File:

```text
frontend/src/services/api.js
```

Functions:

```text
analyzeImage(image, message)
getTasks()
createTask(task)
updateTask(id, data)
```

All HTTP calls should be centralized here.

---

# 22. Frontend Components

## ImageUploader

Responsibilities:

- drag/drop optional
- file picker
- validation
- image preview
- submit

## AgentActivity

Display:

```text
✓ Image understood
✓ Problem identified
✓ Action plan generated
✓ Checklist generated
✓ Task created
```

## ProblemCard

Display:

- category
- title
- problem
- important details

## ActionPlan

Display ordered actions.

## Checklist

Display checkboxes.

## TaskList

Display SQLite-backed tasks.

---

# 23. Frontend State

Use React state.

Minimum:

```text
selectedImage
previewUrl
message
loading
error
result
agentActivity
tasks
```

Do not introduce Redux.

---

# 24. UI States

## Initial

Show upload area.

## Image selected

Show preview.

## Processing

Show:

```text
FixIt is working...

Understanding image
Selecting actions
Preparing result
```

## Success

Show result cards.

## Error

Show useful error state.

## Empty task list

Show:

"No tasks yet."

---

# 25. Styling

Design goals:

- clean
- modern
- premium
- student-friendly
- calm
- clear hierarchy

Avoid:

- excessive gradients
- fake AI neon
- huge dashboard
- unnecessary charts
- template-like admin UI

The hero interaction must communicate:

```text
IMAGE
  ↓
FIXIT
  ↓
ACTION
```

---

# 26. Demo Fixtures

Create:

```text
demo/technical_error.png
demo/sample_notice.png
```

If image generation is not practical inside the coding environment, create text instructions for the user to supply screenshots manually.

The notice should be explicitly labeled as sample/demo content and should not falsely represent official CKPCET policy.

---

# 27. Testing Plan

## Backend

Test:

- health endpoint
- task creation
- task retrieval
- task update
- invalid task
- database persistence

## AI

Test:

- image input
- image + message
- function call
- tool execution
- final response
- API error

## Frontend

Test:

- image upload
- preview
- loading
- success
- error
- task display
- task completion

---

# 28. End-to-End Acceptance Tests

### Test A

Input:

Technical error screenshot.

Expected:

```text
Image understood
Problem identified
Action plan generated
Checklist generated
```

### Test B

Input:

Sample college notice.

Expected:

```text
Notice understood
Deadline extracted
Actions generated
Checklist generated
```

Then:

```text
Create Tasks
```

Expected:

```text
Tasks inserted into SQLite
Tasks visible in UI
```

### Test C

Refresh.

Expected:

Tasks remain.

### Test D

Complete task.

Expected:

SQLite completion state changes.

---

# 29. Error Handling

Handle:

- 400 invalid image
- 413 oversized image
- 422 validation errors
- 500 model error
- database failure

Frontend should translate technical errors into human-readable messages.

Log useful diagnostics on backend without logging secrets.

---

# 30. Requirements File

Minimum dependencies should be similar to:

```text
fastapi
uvicorn
python-multipart
pydantic
python-dotenv
google-genai
```

Pin versions after installing/testing if appropriate.

Do not add packages without a reason.

---

# 31. Local Run

Backend:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

The exact Windows command can be documented according to the environment.

---

# 32. Git Requirements

`.gitignore`:

```text
.env
venv/
.venv/
__pycache__/
*.pyc
node_modules/
dist/
*.db
```

If the SQLite database needs to be demonstrated as persistent sample state, decide explicitly whether a seeded database is committed. Do not accidentally commit personal/generated data.

---

# 33. Open-Source Requirements

Create:

```text
LICENSE
README.md
```

Use MIT license unless the event or dependencies impose a different requirement.

README must explain:

- purpose
- architecture
- setup
- environment
- AI model
- tools
- safety boundaries
- demo
- project structure
- license

---

# 34. Implementation Priority

## P0

1. FastAPI
2. image upload
3. Gemma multimodal call
4. tool calling
5. analyze_image
6. action plan
7. checklist
8. task creation
9. SQLite
10. React result UI

## P1

11. polished agent activity
12. task completion
13. error handling
14. README
15. demo fixtures

## P2

16. animations
17. extra visual polish

Stop immediately if P2 threatens P0/P1 reliability.

---

# 35. Definition of Done

The implementation is complete when:

- frontend runs
- backend runs
- image reaches backend
- Gemma processes image
- model can request registered tool(s)
- backend executes tools
- results return to model/application
- actionable response appears
- tasks persist
- UI shows agent activity
- errors are handled
- secrets are protected
- README works
- LICENSE exists
- demo can be completed within 2 minutes

---

# 36. Technical Principle

The most important architecture rule:

**The model decides. The application executes.**

That keeps the agent explainable, testable and safe.
