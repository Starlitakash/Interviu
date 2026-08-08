# Interviu — Adaptive AI Technical Interviewer

> **An AI interviewer that remembers what you learned.**

Interviu is a personalized technical interviewer built for the **ABTalks AI Cohort**. It turns a candidate's profile, learning journey, completed missions, curriculum topics, objectives, and interview responses into a curriculum-grounded interview that adapts one answer at a time.

## Live Demo

**[Open Interviu](https://interviu-573j.onrender.com)** · [Production API](https://interviu-573j.onrender.com/api/interview) · [Swagger Docs](https://interviu-573j.onrender.com/docs)

> The app runs on Render's free tier. If it has been inactive, the first request may take a few seconds to spin up—please wait briefly and refresh.

## Problem

Finishing a technical AI course does not always translate into confidently explaining what was built or why particular engineering decisions were made. Generic interviews compound the problem: they cannot distinguish between topics a learner completed, concepts they only partially understand, and skills they have not encountered yet.

## Solution

Interviu conducts a candidate-specific interview from the learner's actual journey. It retrieves relevant curriculum context, plans topics and objectives, asks grounded questions, evaluates each response, and selects the appropriate next move. The result is an interview that is personal, adaptive, and tied to what the candidate learned.

## Key Features

- Personalized interview context from profiles, learning journeys, missions, and curriculum objectives.
- In-memory keyword retrieval for curriculum-grounded questions.
- LangGraph-powered orchestration for stateful interview flow.
- Adaptive follow-ups based on response quality.
- Meaningless-answer detection for empty, short, or non-substantive responses.
- Candidate-specific final feedback with scores, strengths, gaps, coverage, and next steps.
- REST API with interactive OpenAPI/Swagger documentation.

## Adaptive Interviewing

| Candidate response | Interviu's next step |
| --- | --- |
| Strong answer | Evaluates the response and asks a deeper follow-up. |
| Partial answer | Identifies missing concepts and asks a targeted follow-up. |
| Meaningless answer (`ok`, `idk`, or empty) | Records the signal and moves forward without assuming competency. |

## Candidate Evaluation

At the end of an interview, Interviu aggregates turn-level evaluations into a report that can include:

- Overall score and hiring recommendation
- Topic-wise performance and curriculum coverage
- Strengths and areas for growth
- Interview statistics
- Recommended next steps

## System Architecture

```text
Candidate Profile
        │
        ▼
Curriculum Retrieval → Interview Planner → Question Generator
                                             │
                                             ▼
                                      Candidate Response
                                             │
                                             ▼
Response Evaluator → Follow-Up / Topic Transition → Interview State
                                                        │
                                                        ▼
                                              Feedback Aggregator
                                                        │
                                                        ▼
                                                   Final Report
```

## LangGraph Workflow

```text
Interview Request
  → Session Initialization
  → Curriculum Retrieval
  → Interview Planning
  → Question Generation
  → Candidate Response
  → Response Evaluation
  → Conditional Routing
      ├─ Strong       → Deeper Follow-Up
      ├─ Partial      → Missing-Concept Follow-Up
      ├─ Meaningless  → Move Forward
      └─ Complete     → Final Feedback → Final Evaluation Report
```

## Tech Stack

| Area | Technology |
| --- | --- |
| Frontend | HTML, CSS, JavaScript |
| Backend | FastAPI, Uvicorn |
| LLM | Groq |
| AI orchestration & state | LangGraph / Session State |
| Retrieval | In-memory keyword retrieval |
| Validation | Pydantic |
| API documentation | OpenAPI / Swagger |
| Testing | Pytest |
| Deployment | Render |
| Version control | Git + GitHub |

## Project Structure

```text
Interviu/
├── app/
│   ├── config/       # Environment settings & constraints
│   ├── schemas/      # Pydantic validation schemas & interview state
│   ├── models/       # Domain dataclasses
│   ├── utils/        # LLM clients, loggers, and formatters
│   ├── retrieval/    # Curriculum chunker & in-memory keyword retriever
│   ├── evaluation/   # Difficulty controller & coverage checkers
│   ├── prompts/      # Role-anchored templates
│   ├── agents/       # Planner, generator, evaluator & feedback agents
│   ├── graph/        # LangGraph workflows & conditional routing
│   ├── services/     # Session manager & interview engine
│   ├── routers/      # FastAPI REST endpoints
│   └── main.py       # FastAPI application entrypoint
├── tests/            # Unit & API integration tests
├── PROMPTS.md        # Continuous AI usage hackathon log
├── implementation_plan.md
├── requirements.txt
├── LICENSE
└── README.md
```

## API Documentation

### `POST /api/interview`

Start an interview by sending a session ID and candidate profile:

```json
{
  "sessionId": "candidate-session-001",
  "candidate": {
    "...": "candidate profile"
  }
}
```

Continue the same interview with the candidate's answer:

```json
{
  "sessionId": "candidate-session-001",
  "message": "Candidate's technical answer..."
}
```

Example ongoing response:

```json
{
  "reply": "Next interview question...",
  "done": false,
  "feedback": null
}
```

When the interview is complete, the response includes the final evaluation:

```json
{
  "reply": "Interview completed.",
  "done": true,
  "feedback": {
    "summary": "...",
    "strengths": [],
    "gaps": [],
    "next": [],
    "overall_score": 0,
    "hiring_recommendation": "...",
    "topic_breakdown": [],
    "interview_statistics": {}
  }
}
```

Explore the full interactive contract at [Swagger Docs](https://interviu-573j.onrender.com/docs).

## Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/Interviu.git
cd Interviu
```

Create and activate a virtual environment:

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

Install dependencies and set your Groq API key:

```bash
pip install -r requirements.txt
```

```env
GROQ_API_KEY=your_api_key_here
```

Run the application:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- Application: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

## Deployment

Interviu is deployed on [Render](https://interviu-573j.onrender.com). Configure `GROQ_API_KEY` as an environment variable in your deployment environment; do not place it in source code.

## Testing

```bash
python -m pytest -v
```

## Key Design Decisions

- **Curriculum grounding:** Retrieval ties interview questions to the learner's completed curriculum instead of relying on generic prompts.
- **Stateful orchestration:** LangGraph maintains interview context and routes each turn according to the evaluation result.
- **Honest progression:** Meaningless responses trigger forward movement rather than an unsupported claim of demonstrated knowledge.
- **Actionable output:** The final report combines turn-level evaluations into feedback a candidate can use.

## Security

Never commit API keys or `.env` files to GitHub. Keep secrets such as `GROQ_API_KEY` in local environment files and deployment-platform environment variables.

## License

This project is licensed under the [MIT License](LICENSE).

## Author

**Akash Singh**  
Built for the **ABTalks AI Cohort**.
