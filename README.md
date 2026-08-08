# 🎯 Interviu — Adaptive AI Technical Interviewer

> **An AI interviewer that remembers what you learned.**

Interviu is an adaptive AI technical interviewer built for the **ABTalks AI Cohort**.

Instead of asking every candidate the same generic questions, Interviu uses the candidate's **profile, learning journey, completed missions, curriculum objectives, and previous answers** to conduct a personalized technical interview.

The system adapts follow-up questions based on the candidate's responses and generates an evidence-based technical evaluation at the end of the interview.

---

## 🚀 Live Demo

🌐 **[Try Interviu →](https://interviu-573j.onrender.com)**

> ⚠️ **Note:** The application is hosted on Render's free tier. If the service has been inactive, the first request may take a few seconds while the server spins up. Please wait a moment and refresh if necessary.

---

## 💡 The Problem

Traditional technical interview preparation often follows:

**Generic Questions → Same Interview For Everyone → Generic Evaluation → Generic Feedback**

This approach does not consider what a candidate actually learned during their learning journey.

A candidate may have completed different topics and have different strengths and weaknesses, but a traditional interview often treats everyone the same.

---

## 🧠 The Solution

Interviu turns the candidate's learning journey into an adaptive technical interview.

**Candidate Profile**

↓

**Learning Journey + Curriculum Objectives**

↓

**Personalized Interview Plan**

↓

**Curriculum-Grounded Questions**

↓

**Candidate Response**

↓

**Evidence-Based Evaluation**

↓

**Adaptive Follow-Up**

↓

**Personalized Interview Report**

### Core Idea

> **The interview adapts to what the candidate actually learned.**

A strong answer can lead to a deeper follow-up.

A partial answer can trigger a question targeting missing concepts.

A meaningless response is detected and the system can move forward instead of incorrectly treating it as demonstrated competency.

---

# ✨ Key Features

### 🎓 Curriculum-Grounded Interviews

Questions are generated around the candidate's actual learning journey and curriculum objectives.

**Candidate Profile → Completed Missions → Curriculum Topics → Learning Objectives → Interview Questions**

---

### 🔄 Adaptive Interviewing

The interview is not a fixed sequence of questions.

**Strong Answer**

Strong Response → Strong Evaluation → Deeper Follow-Up

**Partial Answer**

Partial Response → Missing Concepts Identified → Targeted Follow-Up

**Meaningless Answer**

`"ok"` / `"idk"` / empty response → Meaningless Response Detection → Move Forward

---

### 📊 Evidence-Based Evaluation

Each response is evaluated using multiple signals such as:

- Concept coverage
- Technical depth
- Practical reasoning
- Implementation understanding
- Missing concepts
- Response quality

Turn-level evaluations are aggregated into the final candidate report.

---

### 🎯 Candidate-Specific Reports

After the interview, Interviu generates a structured evaluation containing:

- Overall score
- Hiring recommendation
- Topic-wise performance
- Strengths
- Areas for growth
- Curriculum coverage
- Interview statistics
- Recommended next steps

---

# 🏗️ System Architecture

```
                    Candidate Profile
                           │
                           ▼
                 Curriculum Retrieval
                           │
                           ▼
                  Interview Planner
                           │
                           ▼
                 Question Generator
                           │
                           ▼
                  Candidate Response
                           │
                           ▼
                  Response Evaluator
                           │
                 ┌─────────┴─────────┐
                 │                   │
                 ▼                   ▼
          Follow-Up Question    Topic Transition
                 │                   │
                 └─────────┬─────────┘
                           │
                           ▼
                   Interview State
                           │
                           ▼
                  Feedback Aggregator
                           │
                           ▼
                    Final Report
```

---

# 🔄 LangGraph Workflow

The interview orchestration is implemented using **LangGraph**.

```
Interview Request
       ↓
Session Initialization
       ↓
Curriculum Retrieval
       ↓
Interview Planning
       ↓
Question Generation
       ↓
Candidate Response
       ↓
Response Evaluation
       ↓
Conditional Routing
       │
       ├── Strong → Deeper Follow-Up
       │
       ├── Partial → Missing Concept Follow-Up
       │
       ├── Meaningless → Move Forward
       │
       └── Complete → Final Feedback
       ↓
Final Evaluation Report
```

LangGraph allows the interview to behave as a stateful and conditional workflow instead of a simple linear LLM conversation.

---

# 🛠️ Tech Stack

CategoryTechnologies🎨 FrontendHTML, CSS, JavaScript⚡ BackendFastAPI, Uvicorn🤖 LLMGroq🔄 AI OrchestrationLangGraph📋 Data ValidationPydantic🔎 RetrievalIn-memory keyword retrieval🧠 State ManagementLangGraph / Session State🔌 APIREST API📚 API DocumentationOpenAPI / Swagger🧪 TestingPytest📦 Dependenciesrequirements.txt🚀 DeploymentRender🗂️ Version ControlGit + GitHub

---

# 📁 Project Structure

```
Interviu/
│
├── app/
│   ├── config/              # Environment settings & constraints
│   ├── schemas/             # Pydantic validation schemas & InterviewState
│   ├── models/              # Domain dataclasses
│   ├── utils/               # LLM clients, loggers & formatters
│   ├── retrieval/           # Curriculum chunker & in-memory keyword retriever
│   ├── evaluation/          # Difficulty controller & coverage checkers
│   ├── prompts/             # Role-anchored templates
│   ├── agents/              # Planner, Generator, Evaluator & Feedback agents
│   ├── graph/               # LangGraph workflows & conditional routing
│   ├── services/            # Session manager & interview engine
│   ├── routers/             # FastAPI REST endpoints
│   └── main.py              # FastAPI application entrypoint
│
├── tests/                   # Pytest unit & API integration test suite
├── PROMPTS.md               # Continuous AI usage hackathon log
├── implementation_plan.md   # Engineering design blueprint
├── requirements.txt         # Python dependency manifest
├── LICENSE                  # MIT License
└── README.md                # Project documentation
```

---

# 🔌 API

Interviu exposes a unified interview interface:

### `POST /api/interview`

The endpoint allows an external client or evaluator to interact with the interview agent without depending on the frontend.

### Start an Interview

```
{
  "sessionId": "candidate-session-001",
  "candidate": {
    "...": "candidate profile"
  }
}
```

### Continue an Interview

Use the same `sessionId`:

```
{
  "sessionId": "candidate-session-001",
  "message": "Candidate's technical answer..."
}
```

### Ongoing Response

```
{
  "reply": "Next interview question...",
  "done": false,
  "feedback": null
}
```

### Completed Interview

```
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

---

# 📚 API Documentation

Interactive Swagger/OpenAPI documentation:

**Local:**

[http://localhost:8000/docs](http://localhost:8000/docs)

**Production:**

[https://interviu-573j.onrender.com/docs]()

---

# 💻 Run Locally

### 1. Clone the Repository

```
git clone https://github.com/YOUR_USERNAME/Interviu.git
cd Interviu
```

### 2. Create a Virtual Environment

**Windows:**

```
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**

```
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```
GROQ_API_KEY=your_api_key_here
```

> ⚠️ Never commit API keys, `.env` files, or other secrets to GitHub.

### 5. Start the Server

```
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open the application:

[http://localhost:8000](http://localhost:8000)

Open Swagger:

[http://localhost:8000/docs](http://localhost:8000/docs)

---

# ☁️ Deployment

Interviu is deployed using **Render**.

### 🌐 Live Application

[https://interviu-573j.onrender.com](https://interviu-573j.onrender.com)

### 🔌 Production API

[https://interviu-573j.onrender.com/api/interview]()

### 📚 Production API Documentation

[https://interviu-573j.onrender.com/docs]()

> ⚠️ **Render Cold Start:** Since the application is hosted on Render's free tier, the service may sleep after inactivity. The first request may take a little longer while the server spins up. Please wait a few seconds and refresh if necessary.

---

# 🧪 Testing

The repository contains unit and API integration tests in:

```
tests/
```

The complete interview flow can be tested as:

```
Candidate Profile
       ↓
Interview Initialization
       ↓
Question Generation
       ↓
Candidate Response
       ↓
Response Evaluation
       ↓
Adaptive Follow-Up
       ↓
Topic Transition
       ↓
Interview Completion
       ↓
Final Report
```

Important test scenarios include:

- Candidate initialization
- Session continuity
- Strong technical answers
- Partial answers
- Meaningless answers
- Adaptive follow-ups
- Curriculum-grounded questions
- API integration
- Final feedback generation

---

# 🧠 Key Design Decisions

## Why LangGraph?

The interview is a stateful and conditional workflow rather than a simple linear LLM conversation.

LangGraph coordinates:

- Interview state
- Planning
- Question generation
- Response evaluation
- Conditional routing
- Adaptive follow-ups
- Interview completion

## Why Curriculum-Grounded Questions?

A generic LLM can generate technically valid questions that are unrelated to what a candidate actually learned.

Interviu grounds questions in the cohort curriculum and learning objectives so candidates are evaluated on relevant knowledge.

## Why Evaluate Individual Responses?

A final score alone does not explain candidate competency.

Turn-level evaluation provides evidence that can be aggregated into:

```
Candidate Responses
        ↓
Response Evaluations
        ↓
Topic Performance
        ↓
Overall Evaluation
        ↓
Final Report
```

## Why Detect Meaningless Responses?

Responses such as:

```
"ok"
"idk"
"yes"
```

should not be interpreted as demonstrated technical competency.

Interviu detects very short or meaningless responses and adjusts the interview flow accordingly.

---

# 🎯 Product Flow

```
             ABTalks AI Cohort
                    ↓
             Candidate Profile
                    ↓
          Personalized Interview
                    ↓
           Adaptive Questions
                    ↓
          Response Evaluation
                    ↓
          Competency Analysis
                    ↓
              Final Report
                    ↓
             Learning Gaps
                    ↓
          Recommended Next Steps
```

### Learn → Build → Interview → Evaluate → Improve

---

# 📜 License

This project is licensed under the **MIT License**.

See the [`LICENSE`](LICENSE) file for details.

---

# 👨‍💻 Author

**Akash Singh**

Built for the **ABTalks AI Cohort**.

---

> **Interviu — Learn → Build → Interview → Evaluate → Improve.**
