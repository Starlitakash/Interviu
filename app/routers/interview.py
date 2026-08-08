from fastapi import APIRouter, HTTPException, status
from app.schemas.requests import (
    StartInterviewRequest,
    SubmitAnswerRequest,
    EndInterviewRequest,
    UnifiedInterviewRequest
)
from app.schemas.responses import (
    StartInterviewResponse,
    SubmitAnswerResponse,
    EndInterviewResponse,
    SessionStatusResponse,
    UnifiedInterviewResponse
)
from app.services.interview_service import interview_service

router = APIRouter(tags=["Interview"])

# ── Primary Hackathon Endpoint (technical-spec.md) ──
@router.post("/api/interview", response_model=UnifiedInterviewResponse, status_code=status.HTTP_200_OK)
def handle_unified_interview_endpoint(req: UnifiedInterviewRequest):
    """
    Primary API endpoint matching technical-spec.md requirements.
    Handles start, conversation turns, and completion feedback via POST /api/interview.
    """
    try:
        return interview_service.handle_unified_interview(req)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# ── Granular REST Endpoints ──
@router.post("/interview/start", response_model=StartInterviewResponse, status_code=status.HTTP_200_OK)
def start_interview(req: StartInterviewRequest):
    """Initialize a new adaptive AI interview session with granular metadata."""
    try:
        return interview_service.start_interview(req)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/interview/answer", response_model=SubmitAnswerResponse, status_code=status.HTTP_200_OK)
def submit_answer(req: SubmitAnswerRequest):
    """Submit candidate's answer and receive next question or final feedback with granular scores."""
    try:
        return interview_service.submit_answer(req)
    except ValueError as ve:
        err_msg = str(ve)
        if "not found" in err_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_msg)
        if "already completed" in err_msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/interview/end", response_model=EndInterviewResponse, status_code=status.HTTP_200_OK)
def end_interview(req: EndInterviewRequest):
    """Force-end an active interview session early and receive feedback report."""
    try:
        return interview_service.end_interview(req.session_id)
    except ValueError as ve:
        err_msg = str(ve)
        if "not found" in err_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

@router.get("/interview/status/{session_id}", response_model=SessionStatusResponse, status_code=status.HTTP_200_OK)
def get_interview_status(session_id: str):
    """Get real-time monitoring and state metrics for an active session."""
    try:
        return interview_service.get_status(session_id)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
