# FIXIT — Product Requirements Document (PRD)

**Version:** 1.0  
**Date:** 03 October 2026  
**Project:** FixIt — See a problem. Get an action.  
**Hackathon:** MLH Hacktoberfest Hack Day Surat 2026  
**Primary Challenges:** Best Use of Gemma 4; Best Open-Source AI Project

---

## 1. Executive Summary

FixIt is a multimodal AI action agent that accepts an image such as a software error screenshot, college notice, assignment sheet, instruction page, or other actionable visual information and converts it into concrete next steps.

FixIt is intentionally not a generic image captioning tool and not a normal chatbot.

Its core loop is:

**See → Understand → Decide → Act**

1. The user provides an image and optionally a short request.
2. Gemma 4 interprets the visual information and user intent.
3. The agent determines which registered capabilities are required.
4. The backend validates and executes those capabilities.
5. Results are stored or generated as appropriate.
6. FixIt presents a concise, actionable result to the user.

The primary hackathon value is demonstrating that multimodal AI can move from visual understanding to real application actions.

---

# 2. Problem Statement

People frequently receive important information visually:

- error screenshots
- college notices
- assignment sheets
- instructions
- forms
- project requirements
- warning messages
- schedules
- task descriptions

Existing AI experiences often stop at:

> "This image contains..."

That is useful for understanding, but not enough for action.

The user still has to determine:

- What is the actual problem?
- What should I do next?
- What are the individual actions?
- What should I remember?
- What should become a task?

FixIt addresses this gap.

### Problem

**Visual information is often understandable but not immediately actionable.**

### Solution

**FixIt converts visual information into structured actions and, where appropriate, real application state such as tasks.**

---

# 3. Product Vision

FixIt should become a reusable multimodal action-agent pattern:

> Give FixIt something you need to understand. FixIt figures out what needs to happen next.

The MVP is intentionally narrow enough to build reliably during a short hackathon sprint.

---

# 4. Hackathon Alignment

## 4.1 Best Use of Gemma 4

The product uses Gemma 4 as an important part of the core workflow.

The intended experience demonstrates:

- multimodal image understanding
- agent/tool selection
- structured actions
- real tool execution
- actionable output

Gemma is therefore not decorative or used only for generating a final paragraph.

It participates in the decision-making layer of the product.

Google's current Gemini API documentation supports multimodal model interactions and function calling, where the model can request registered functions and the application executes them. The official Interactions API documentation currently lists `gemma-4-26b-a4b-it` and `gemma-4-31b-it` as available Gemma 4 models. The exact model selected at implementation time must be verified against the live API/model availability before the hackathon submission. 

## 4.2 Best Open-Source AI Project

FixIt will be published as a public GitHub repository with an open-source license.

The repository should contain:

- agent orchestration
- tool declarations
- tool implementations
- multimodal model integration
- frontend
- backend
- setup instructions
- architecture documentation

The AI/model integration must be a meaningful part of the application rather than a superficial API wrapper.

---

# 5. Target Users

### Primary

- college students
- developers
- project teams
- hackathon participants

### Secondary

- teachers/students handling notices
- users dealing with instructions or screenshots
- general users who need help turning visual information into actions

---

# 6. MVP Scope

The MVP has four core capabilities:

1. Image understanding / classification
2. Action-plan generation
3. Checklist generation
4. Task creation and persistence

The agent may use one or multiple capabilities for a single request.

---

# 7. Core User Stories

## US-01 — Upload an image

As a user, I want to upload a screenshot or photo so FixIt can understand it.

Acceptance criteria:

- image can be selected from the browser
- image preview is shown
- supported image types are validated
- user can optionally add text
- image can be submitted to the agent

---

## US-02 — Understand a technical error

As a developer/student, I want to upload an error screenshot and receive a useful diagnosis and action plan.

Example:

`ModuleNotFoundError: No module named 'fastapi'`

Expected:

- identify the problem
- explain it simply
- provide a safe recommended fix
- generate a checklist

FixIt must not execute arbitrary commands merely because a model generated them.

---

## US-03 — Understand a college notice

As a student, I want to upload a notice and have FixIt identify deadlines and required actions.

Expected:

- notice type identified
- important date extracted when visible
- actions listed
- checklist generated
- user can create tasks

---

## US-04 — Create real tasks

As a user, I want actionable items extracted from an image to become persistent tasks.

Expected:

- task stored in SQLite
- task appears immediately in UI
- task remains after refresh
- completion state can be changed

---

## US-05 — See what the agent did

As a user/judge, I want to understand the agent's observable workflow.

Expected UI:

- Image understood
- Problem identified
- Action plan generated
- Checklist generated
- Task created

Do not expose hidden chain-of-thought.

---

# 8. Primary Demo

## Demo A — Technical Screenshot

Input image:

A realistic screenshot containing:

`ModuleNotFoundError: No module named 'fastapi'`

Expected flow:

1. Upload image.
2. Gemma interprets image.
3. Agent identifies technical error.
4. Action plan is generated.
5. Checklist is generated.
6. Result is displayed.

Example result:

**Problem detected**

A required Python dependency is missing.

**Recommended action**

Install FastAPI in the active environment and verify the environment before running the project again.

**Checklist**

- Install missing dependency
- Verify active environment
- Run the application again

No arbitrary command execution.

---

## Demo B — College Notice

Input image:

A clearly labeled sample college notice such as:

"Semester 6 students must submit their project report by October 8."

Expected:

**Notice understood**

Deadline: October 8

Actions:

- Complete project report
- Print final copy
- Submit before deadline

User selects:

**Create Tasks**

Tasks are persisted in SQLite.

The UI displays:

`✓ 3 tasks created`

---

# 9. Functional Requirements

## FR-01 Image Input

The frontend shall accept an image.

Supported MVP formats:

- PNG
- JPG/JPEG
- WEBP if supported by the selected API/client

The backend must validate file type and size.

---

## FR-02 Optional User Instruction

The user may provide additional text.

Examples:

- "What should I do?"
- "Explain this error."
- "Turn this notice into tasks."
- "What is my deadline?"

---

## FR-03 Multimodal Analysis

The backend shall send relevant image content and user instruction to the selected Gemma/Gemini API.

The model must receive sufficient context to understand both visual content and user intent.

---

## FR-04 Agent Decision

The agent shall determine whether one or more registered capabilities are useful.

Possible capabilities:

- analyze_image
- generate_action_plan
- generate_checklist
- create_task

---

## FR-05 Tool Execution

The backend, not the model, executes the selected tool.

The application must:

1. receive function call
2. validate function name
3. validate arguments
4. execute registered implementation
5. capture result
6. return result to the model when a final response is needed

Google's function-calling documentation explicitly defines this separation: the model requests a function call, while the application is responsible for executing the function and returning the result. It also supports sequential/compositional and multiple tool calls. 

---

## FR-06 Action Plan

The action plan should contain:

- short summary
- ordered actions
- priority when meaningful

The plan must remain grounded in available evidence.

---

## FR-07 Checklist

The checklist shall convert actionable information into concise items.

---

## FR-08 Task Creation

Tasks shall contain:

- title
- description
- category
- deadline if known
- completed state
- created timestamp

---

## FR-09 Task Persistence

Tasks shall survive:

- page refresh
- frontend restart
- backend restart

provided the SQLite database file remains available.

---

## FR-10 Task Completion

User can mark a task complete/incomplete.

---

## FR-11 Agent Activity

The frontend shall display observable execution status.

Example:

- Image understood
- Problem identified
- Action plan generated
- Checklist generated
- Task created

No hidden reasoning text.

---

# 10. Non-Functional Requirements

## NFR-01 Reliability

The main two demo flows must work repeatedly.

## NFR-02 Simplicity

Architecture must remain understandable to a college student.

## NFR-03 Security

No API key in frontend or Git repository.

No arbitrary code execution.

No arbitrary SQL execution.

## NFR-04 Responsiveness

UI should provide loading feedback during model calls.

## NFR-05 Maintainability

AI logic, tools, API routes, database, and UI should be separated.

## NFR-06 Hackathon Readiness

The application must be runnable locally with documented setup steps.

---

# 11. Out of Scope

Do not build these in the MVP:

- authentication
- user accounts
- admin panel
- faculty portal
- mobile application
- email
- WhatsApp
- push notifications
- calendar integration
- browser automation
- arbitrary shell execution
- arbitrary code execution
- RAG/vector database
- embeddings
- multiple autonomous agents
- cloud deployment unless the core product is already complete
- complex analytics
- production-grade multi-user infrastructure

---

# 12. User Experience

## Landing / Main View

Brand:

**FIXIT**

Tagline:

**See a problem. Get an action.**

Primary interface:

- image upload/drop area
- image preview
- optional instruction field
- Analyze button

---

# 13. Result Experience

Results should be visually separated into:

### Problem

What was detected.

### Action Plan

What the user should do.

### Checklist

What can be checked off.

### Tasks

What was persisted into the application.

---

# 14. Error States

If no image:

"Please upload an image first."

If unsupported format:

"Please upload a PNG, JPG, JPEG, or supported image."

If model/API failure:

"FixIt could not process this image right now. Check the AI configuration and try again."

If no actionable information:

"I could understand the image, but I could not identify a reliable action from it."

If task creation fails:

"Your analysis succeeded, but the task could not be saved."

Never claim success when the backend operation failed.

---

# 15. Demo Success Criteria

The project is considered demo-ready when:

### Scenario 1

Image → Gemma → Agent → action plan → checklist

works end-to-end.

### Scenario 2

Notice image → Gemma → extracted action/deadline → task creation → SQLite → UI

works end-to-end.

### Scenario 3

Refresh → tasks remain.

---

# 16. Success Metrics for the Hackathon

These are product validation targets, not claims:

- both demo scenarios work reliably
- multimodal input is visibly used
- Gemma is visibly part of the core flow
- at least one real tool changes persistent application state
- repository is public and licensed
- setup works from README
- 2-minute demo can be completed without manual database edits

---

# 17. Future Scope

Possible future versions:

- PDF/document input
- voice input
- calendar integration
- campus-specific workflows
- smarter task prioritization
- real notification integrations
- browser-assisted workflows with explicit user approval
- multiple action domains
- reusable agent-skill/plugin architecture

These are NOT part of the hackathon MVP.

---

# 18. Product Principle

FixIt should always answer:

> "What should happen next?"

rather than merely:

> "What is in this image?"

That distinction is the product.
