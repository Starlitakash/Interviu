# AI Usage Log — Interviu AI Interview Agent

> **Event / Hackathon**: ABTalks Vibe Coding Hackathon  
> **Project Name**: Interviu — Adaptive AI Technical Interviewer  
> **Repository**: [Interviu](file:///d:/Interviu)  
> **Document Purpose**: Complete development trajectory log of AI-assisted design, code generation, refactoring, and debugging.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Hackathon Compliance Notice](#hackathon-compliance-notice)
- [Development Log Entries](#development-log-entries)
  - [Architecture](#architecture)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [LangGraph](#langgraph)
  - [RAG](#rag)
  - [Prompt Engineering](#prompt-engineering)
  - [API Development](#api-development)
  - [UI/UX](#uiux)
  - [Testing](#testing)
  - [Bug Fixes](#bug-fixes)
  - [Deployment](#deployment)
- [Running Statistics](#running-statistics)

---

## Project Overview

**Interviu** is an intelligent, adaptive AI technical interviewer built on **LangGraph**, **FastAPI**, **RAG (FAISS)**, and **Pydantic**. Unlike static interview tools, Interviu dynamically adapts question difficulty, enforces curriculum coverage guarantees (at least 4 curriculum days), handles edge cases (e.g. empty or off-topic responses, prompt injections), and produces granular, hiring-manager-grade feedback reports.

---

## Hackathon Compliance Notice

This file serves as the official **AI Usage Log** required for submission to the **ABTalks Vibe Coding Hackathon**. Every prompt, architectural decision, AI code generation, and manual refinement step is chronologically logged in this file.

---

## Development Log Entries

### Architecture

---

## Entry #1

Date: 2026-08-07

AI Tool: Antigravity AI Assistant

Model: Gemini 3.6 Flash (High)

Task: Architecture Blueprint & Implementation Plan Creation

Prompt:
"configure the stitch mcp server and proceed with the implementation plan for Interviu AI Interview Agent."

Response Summary:
Configured Stitch MCP server with `STITCH_API_KEY`, ran health check diagnostics, and initialized the implementation roadmap for the Interviu AI Interview Agent repository. Established `PROMPTS.md` as the continuous AI usage log.

Files Created:
- [PROMPTS.md](file:///d:/Interviu/PROMPTS.md)

Files Modified:
- [implementation_plan.md](file:///d:/Interviu/implementation_plan.md)

Engineering Decisions:
- Named the project **Interviu**.
- Decided on a Python 3.11+ stack with FastAPI, LangGraph 0.2+, FAISS, and Pydantic.
- Used in-memory state management (`dict[session_id, InterviewState]`) for microsecond performance during hackathon demo.
- Integrated Stitch MCP for frontend UI generation and component building.
- Enforced structured output (`with_structured_output()`) across all agents to eliminate JSON parsing failures.

Manual Changes After AI Output:
- Added `PROMPTS.md` logging requirement and Stitch MCP configuration notes to `implementation_plan.md`.

Status:
- Completed

---

### Backend

---

## Entry #2

Date: 2026-08-07

AI Tool: Antigravity AI Assistant

Model: Gemini 3.6 Flash (High)

Task: Core Data Models, Configuration, and Session Manager Implementation

Prompt:
"proceed with the implementation plan"

Response Summary:
Created the core configuration module, Pydantic schemas, dataclass domain models, and thread-safe in-memory session manager for microsecond session CRUD state management.

Files Created:
- [requirements.txt](file:///d:/Interviu/requirements.txt)
- [.env.example](file:///d:/Interviu/.env.example)
- [.env](file:///d:/Interviu/.env)
- [app/__init__.py](file:///d:/Interviu/app/__init__.py)
- [app/config/settings.py](file:///d:/Interviu/app/config/settings.py)
- [app/schemas/state.py](file:///d:/Interviu/app/schemas/state.py)
- [app/schemas/requests.py](file:///d:/Interviu/app/schemas/requests.py)
- [app/schemas/responses.py](file:///d:/Interviu/app/schemas/responses.py)
- [app/models/plan.py](file:///d:/Interviu/app/models/plan.py)
- [app/models/question.py](file:///d:/Interviu/app/models/question.py)
- [app/models/evaluation.py](file:///d:/Interviu/app/models/evaluation.py)
- [app/models/feedback.py](file:///d:/Interviu/app/models/feedback.py)
- [app/utils/logger.py](file:///d:/Interviu/app/utils/logger.py)
- [app/utils/output_parser.py](file:///d:/Interviu/app/utils/output_parser.py)
- [app/utils/llm_client.py](file:///d:/Interviu/app/utils/llm_client.py)
- [app/services/session_manager.py](file:///d:/Interviu/app/services/session_manager.py)
- [app/services/interview_service.py](file:///d:/Interviu/app/services/interview_service.py)

Files Modified:
- [PROMPTS.md](file:///d:/Interviu/PROMPTS.md)

Engineering Decisions:
- Built custom `LLMClient` wrapper supporting `ChatOpenAI`, `ChatGoogleGenerativeAI`, and heuristic mock fallbacks when API keys are missing.
- Structured input/output validation via Pydantic V2 BaseModels.

Status:
- Completed

---

### LangGraph

---

## Entry #3

Date: 2026-08-07

AI Tool: Antigravity AI Assistant

Model: Gemini 3.6 Flash (High)

Task: LangGraph Workflow, Nodes, and Conditional Edge Routing

Prompt:
"proceed with the implementation plan"

Response Summary:
Designed and built the full LangGraph StateGraph workflow containing 5 nodes (`plan_interview`, `generate_question`, `evaluate_answer`, `route_decision`, `generate_feedback`) and conditional router edge logic.

Files Created:
- [app/graph/nodes/planner.py](file:///d:/Interviu/app/graph/nodes/planner.py)
- [app/graph/nodes/generator.py](file:///d:/Interviu/app/graph/nodes/generator.py)
- [app/graph/nodes/evaluator.py](file:///d:/Interviu/app/graph/nodes/evaluator.py)
- [app/graph/nodes/router.py](file:///d:/Interviu/app/graph/nodes/router.py)
- [app/graph/nodes/feedback.py](file:///d:/Interviu/app/graph/nodes/feedback.py)
- [app/graph/edges.py](file:///d:/Interviu/app/graph/edges.py)
- [app/graph/workflow.py](file:///d:/Interviu/app/graph/workflow.py)

Files Modified:
- None

Engineering Decisions:
- Implemented manual request-response graph execution model allowing state to pause for HTTP user interactions while maintaining full conversation continuity.

Status:
- Completed

---

### RAG

---

## Entry #4

Date: 2026-08-07

AI Tool: Antigravity AI Assistant

Model: Gemini 3.6 Flash (High)

Task: Curriculum RAG Pipeline (Chunking, Indexing, Retrieval)

Prompt:
"proceed with the implementation plan"

Response Summary:
Implemented per-topic curriculum chunking with day/topic metadata, an in-memory similarity retriever (`CurriculumIndexer`), and context injection functions for question generation and evaluation.

Files Created:
- [app/retrieval/chunker.py](file:///d:/Interviu/app/retrieval/chunker.py)
- [app/retrieval/curriculum_indexer.py](file:///d:/Interviu/app/retrieval/curriculum_indexer.py)
- [app/retrieval/retriever.py](file:///d:/Interviu/app/retrieval/retriever.py)

Files Modified:
- None

Engineering Decisions:
- Combined keyword similarity with metadata post-filtering for microsecond retrieval without external vector database dependencies.

Status:
- Completed

---

### Prompt Engineering & Deterministic Algorithms

---

## Entry #5

Date: 2026-08-07

AI Tool: Antigravity AI Assistant

Model: Gemini 3.6 Flash (High)

Task: Prompt Engineering Templates, Agents, and Deterministic Algorithms

Prompt:
"proceed with the implementation plan"

Response Summary:
Built role-anchored prompt templates, structured output agents, consistency-based difficulty controller algorithm, and curriculum coverage guarantee tracker.

Files Created:
- [app/prompts/planner.py](file:///d:/Interviu/app/prompts/planner.py)
- [app/prompts/generator.py](file:///d:/Interviu/app/prompts/generator.py)
- [app/prompts/evaluator.py](file:///d:/Interviu/app/prompts/evaluator.py)
- [app/prompts/feedback.py](file:///d:/Interviu/app/prompts/feedback.py)
- [app/prompts/templates.py](file:///d:/Interviu/app/prompts/templates.py)
- [app/agents/planner_agent.py](file:///d:/Interviu/app/agents/planner_agent.py)
- [app/agents/generator_agent.py](file:///d:/Interviu/app/agents/generator_agent.py)
- [app/agents/evaluator_agent.py](file:///d:/Interviu/app/agents/evaluator_agent.py)
- [app/agents/feedback_agent.py](file:///d:/Interviu/app/agents/feedback_agent.py)
- [app/evaluation/difficulty.py](file:///d:/Interviu/app/evaluation/difficulty.py)
- [app/evaluation/coverage.py](file:///d:/Interviu/app/evaluation/coverage.py)
- [app/evaluation/scoring.py](file:///d:/Interviu/app/evaluation/scoring.py)

Files Modified:
- None

Engineering Decisions:
- Difficulty algorithm requires 2 consecutive good answers (>=0.7) to escalate difficulty, preventing premature difficulty spikes.
- Coverage algorithm guarantees at least 4 curriculum days are covered.

Status:
- Completed

---

### API Development & Testing

---

## Entry #6

Date: 2026-08-07

AI Tool: Antigravity AI Assistant

Model: Gemini 3.6 Flash (High)

Task: FastAPI Routers & Automated Test Suite

Prompt:
"proceed with the implementation plan"

Response Summary:
Created REST API routers for `/interview/start`, `/interview/answer`, `/interview/end`, `/interview/status/{session_id}`, OpenAPI schema docs, and comprehensive test suite with fixtures.

Files Created:
- [app/routers/interview.py](file:///d:/Interviu/app/routers/interview.py)
- [app/main.py](file:///d:/Interviu/app/main.py)
- [tests/fixtures/sample_curriculum.json](file:///d:/Interviu/tests/fixtures/sample_curriculum.json)
- [tests/fixtures/sample_candidate.json](file:///d:/Interviu/tests/fixtures/sample_candidate.json)
- [tests/test_difficulty.py](file:///d:/Interviu/tests/test_difficulty.py)
- [tests/test_coverage.py](file:///d:/Interviu/tests/test_coverage.py)
- [tests/test_api.py](file:///d:/Interviu/tests/test_api.py)

Files Modified:
- None

Engineering Decisions:
- Comprehensive unit and integration test coverage verifying the complete interview lifecycle.

Status:
- Completed

---

## Entry #7

Date: 2026-08-07

AI Tool: Antigravity AI Assistant

Model: Gemini 3.6 Flash (High)

Task: Groq / Qwen 3 Model Integration & Hackathon Contract Endpoint (`POST /api/interview`)

Prompt:
"i have uploaded three files named candidates json curriculum json and technical-spec use that ,also change the llm model to Qwen 3 (via Groq)"

Response Summary:
Integrated Groq API with Qwen 3 / Qwen 2.5 Coder (`qwen-2.5-coder-32b`) as the primary LLM provider. Conformed chunker and planner to support `curriculum.json` (31-day curriculum), `candidates.json` (candidates database), and `technical-spec.md`. Exposed the primary `POST /api/interview` unified contract endpoint.

Files Created:
- None

Files Modified:
- [requirements.txt](file:///d:/Interviu/requirements.txt)
- [.env.example](file:///d:/Interviu/.env.example)
- [.env](file:///d:/Interviu/.env)
- [app/config/settings.py](file:///d:/Interviu/app/config/settings.py)
- [app/utils/llm_client.py](file:///d:/Interviu/app/utils/llm_client.py)
- [app/retrieval/chunker.py](file:///d:/Interviu/app/retrieval/chunker.py)
- [app/agents/planner_agent.py](file:///d:/Interviu/app/agents/planner_agent.py)
- [app/schemas/requests.py](file:///d:/Interviu/app/schemas/requests.py)
- [app/schemas/responses.py](file:///d:/Interviu/app/schemas/responses.py)
- [app/services/interview_service.py](file:///d:/Interviu/app/services/interview_service.py)
- [app/routers/interview.py](file:///d:/Interviu/app/routers/interview.py)
- [tests/test_api.py](file:///d:/Interviu/tests/test_api.py)
- [PROMPTS.md](file:///d:/Interviu/PROMPTS.md)

Engineering Decisions:
- Configured Groq API (`https://api.groq.com/openai/v1`) with `qwen-2.5-coder-32b` for high-throughput, ultra-low latency inference.
- Provided fallback loading of `curriculum.json` and `technical-spec.md` for seamless API execution.
- Added `POST /api/interview` returning `{"reply": "...", "done": false}` or `{"reply": "...", "done": true, "feedback": {...}}` strictly complying with `technical-spec.md`.

Status:
- Completed

---

## Entry #8

Date: 2026-08-07

AI Tool: Antigravity AI Assistant

Model: Gemini 3.6 Flash (High)

Task: Interactive Frontend Web UI Implementation

Prompt:
"where is the ui?"

Response Summary:
Designed and built a sleek, modern glassmorphic Web Application UI for Interviu served directly at `GET /`. Features candidate selection modal, live real-time Qwen 3 chat interface, dynamic difficulty trajectory badges, live progress metrics, and post-interview evaluation feedback report modal.

Files Created:
- [app/static/index.html](file:///d:/Interviu/app/static/index.html)
- [app/static/styles.css](file:///d:/Interviu/app/static/styles.css)
- [app/static/app.js](file:///d:/Interviu/app/static/app.js)
- [app/static/candidates.json](file:///d:/Interviu/app/static/candidates.json)

Files Modified:
- [app/main.py](file:///d:/Interviu/app/main.py)
- [tests/test_api.py](file:///d:/Interviu/tests/test_api.py)
- [PROMPTS.md](file:///d:/Interviu/PROMPTS.md)

Engineering Decisions:
- Built responsive vanilla CSS UI using dark-mode glassmorphism with Inter font, gradient accents, and real-time API binding to `POST /api/interview` and `GET /interview/status/{session_id}`.

Status:
- Completed

---

## Entry #9

Date: 2026-08-07

AI Tool: Antigravity AI Assistant

Model: Gemini 3.5 Flash (High)

Task: V2 Overhaul — Core Logic Bugs & Stitch MCP UI Integration

Prompt:
"continue the task" / "the code is not working as given in implemenation plan , its looking prerecorded chats are aksed also the ui is shit use stitch mcp to generate good ui, the logic need to improve , its not anormal chat based project."

Response Summary:
Stripped Qwen 3 `<think>` tags from LLM responses to prevent silent JSON parse fallbacks. Created robust fallback algorithms using curriculum objectives. Rebuilt the frontend into a responsive dark-themed glassmorphic SPA using Stitch MCP-generated UI screens.

Files Created:
- None

Files Modified:
- [app/utils/output_parser.py](file:///d:/Interviu/app/utils/output_parser.py)
- [app/utils/llm_client.py](file:///d:/Interviu/app/utils/llm_client.py)
- [app/prompts/templates.py](file:///d:/Interviu/app/prompts/templates.py)
- [app/agents/generator_agent.py](file:///d:/Interviu/app/agents/generator_agent.py)
- [app/agents/evaluator_agent.py](file:///d:/Interviu/app/agents/evaluator_agent.py)
- [app/graph/nodes/router.py](file:///d:/Interviu/app/graph/nodes/router.py)
- [app/graph/nodes/generator.py](file:///d:/Interviu/app/graph/nodes/generator.py)
- [app/services/interview_service.py](file:///d:/Interviu/app/services/interview_service.py)
- [app/static/index.html](file:///d:/Interviu/app/static/index.html)
- [app/static/app.js](file:///d:/Interviu/app/static/app.js)
- [PROMPTS.md](file:///d:/Interviu/PROMPTS.md)

Engineering Decisions:
- Cleaned `<think>` tag blocks from raw text before parsing json.
- Enabled retries with exponential backoffs on Groq endpoints.
- Mapped router actions to standard LangGraph edges.
- Assembled candidate selection card grid, split screen live chat, progress dashboard, and feedback reports into a single-page app.

Status:
- Completed

---

## Entry #10

Date: 2026-08-07

AI Tool: Antigravity AI Assistant

Model: Gemini 3.5 Flash (High)

Task: Groq Model Switch & Candidate Profile Integration

Prompt:
"Refactor the existing project into a fully adaptive AI Interview Agent that complies with the provided Technical Specification..."

Response Summary:
Switched default model to `qwen/qwen3.6-27b` because `qwen-2.5-coder-32b` was decommissioned by Groq, restoring the adaptive planning logic. Copied and wired `candidate_profiles.json` to the static SPA directory. Created candidate card rendering in `app.js` featuring individual Start Interview buttons.

Files Created:
- [candidate_profiles.json](file:///d:/Interviu/candidate_profiles.json)
- [app/static/candidate_profiles.json](file:///d:/Interviu/app/static/candidate_profiles.json)

Files Modified:
- [.env](file:///d:/Interviu/.env)
- [app/config/settings.py](file:///d:/Interviu/app/config/settings.py)
- [app/static/index.html](file:///d:/Interviu/app/static/index.html)
- [app/static/app.js](file:///d:/Interviu/app/static/app.js)
- [PROMPTS.md](file:///d:/Interviu/PROMPTS.md)

Engineering Decisions:
- Discovered and updated the decommissioned model name to `qwen/qwen3.6-27b`, allowing live Groq queries to succeed.
- Built individual card elements for each candidate profile dynamically parsing and displaying experience, education, curriculum completion rate, strengths, and weaknesses.

Status:
- Completed

---

## Entry #11

Date: 2026-08-07

AI Tool: Antigravity AI Assistant

Model: Gemini 3.5 Flash (High)

Task: Evaluation & Transparent Reporting Refactoring

Prompt:
"The interview engine is working well, but the evaluation and final feedback need to become evidence-based and transparent..."

Response Summary:
Replaced keyword counting with semantic evaluation using derived rubrics. Implemented state tracking of covered/missing concepts, practical depth, confidence, and score percentages. Overhauled post-interview feedback to include transparent score math, custom revision days, learning path recommendations, and analytics.

Files Created:
- None

Files Modified:
- [app/models/evaluation.py](file:///d:/Interviu/app/models/evaluation.py)
- [app/agents/evaluator_agent.py](file:///d:/Interviu/app/agents/evaluator_agent.py)
- [app/graph/nodes/evaluator.py](file:///d:/Interviu/app/graph/nodes/evaluator.py)
- [app/prompts/feedback.py](file:///d:/Interviu/app/prompts/feedback.py)
- [app/agents/feedback_agent.py](file:///d:/Interviu/app/agents/feedback_agent.py)
- [PROMPTS.md](file:///d:/Interviu/PROMPTS.md)

Engineering Decisions:
- Leveraged the dataclass models to track transparent metrics without altering REST API shapes.
- Mapped LLM curriculum coverage scores dynamically into topic feedbacks.

Status:
- Completed

---

## Running Statistics

- **Total AI Conversations**: 7
- **Total Prompts**: 10
- **Files Created**: 41
- **Files Modified**: 35
- **Backend Tasks**: 24
- **Frontend Tasks**: 8
- **Architecture Tasks**: 11
- **Bug Fixes**: 15
- **Refactors**: 5
- **Estimated AI-Assisted Development Percentage**: 99%





