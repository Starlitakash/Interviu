import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import interview_router
from app.config.settings import settings

app = FastAPI(
    title="Interviu — Adaptive AI Technical Interviewer",
    description="Stateful, adaptive AI technical interview agent powered by LangGraph, FastAPI, and RAG.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include Routers
app.include_router(interview_router)

@app.get("/", tags=["UI"])
def serve_ui():
    """Serve the Web UI interface."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "status": "healthy",
        "service": "Interviu AI Technical Interviewer API",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """API health status endpoint."""
    return {
        "status": "healthy",
        "service": "Interviu AI Technical Interviewer API",
        "version": "1.0.0",
        "llm_provider": settings.PRIMARY_LLM_PROVIDER
    }
