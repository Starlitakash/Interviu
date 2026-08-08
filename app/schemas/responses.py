from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class QuestionDetail(BaseModel):
    text: str = Field(..., description="The interview question text")
    topic: str = Field(..., description="Topic associated with the question")
    day: str = Field(..., description="Curriculum day identifier")
    difficulty: str = Field(..., description="Difficulty level (easy, medium, etc.)")
    question_number: int = Field(..., description="1-indexed question number")
    question_type: str = Field("conceptual", description="Question type (conceptual, practical, edge_case, etc.)")
    is_followup: bool = Field(False, description="Whether this is a follow-up question")
    context_bridge: Optional[str] = Field(None, description="Conversational bridge from previous answer")

class InterviewPlanSummary(BaseModel):
    total_questions_planned: int = Field(..., description="Total questions budgeted")
    topics_planned: List[str] = Field(..., description="Selected topics")
    days_planned: List[str] = Field(..., description="Selected curriculum days")

class StartInterviewResponse(BaseModel):
    session_id: str
    question: QuestionDetail
    interview_plan: InterviewPlanSummary
    status: str = "in_progress"

class DimensionScores(BaseModel):
    correctness: float = 0.0
    depth: float = 0.0
    reasoning: float = 0.0
    communication: float = 0.0
    practical: float = 0.0
    completeness: float = 0.0

class AnswerEvaluationDetail(BaseModel):
    overall_score: float
    dimension_scores: DimensionScores
    brief_feedback: str
    strengths_noted: List[str] = Field(default_factory=list)
    areas_to_improve: List[str] = Field(default_factory=list)

class ProgressDetail(BaseModel):
    questions_asked: int
    questions_remaining: int
    topics_covered: List[str]
    days_covered: int
    current_difficulty: str

class TopicFeedbackItem(BaseModel):
    topic: str
    day: str
    score: float
    status: str
    summary: str
    key_strengths: List[str] = Field(default_factory=list)
    key_gaps: List[str] = Field(default_factory=list)

class FeedbackReportDetail(BaseModel):
    overall_score: float
    hiring_recommendation: str
    executive_summary: str
    topic_breakdown: List[TopicFeedbackItem]
    strengths: List[str]
    areas_for_growth: List[str]
    actionable_recommendations: List[str]
    interview_statistics: Dict[str, Any]

class SubmitAnswerResponse(BaseModel):
    session_id: str
    evaluation: Optional[AnswerEvaluationDetail] = None
    next_question: Optional[QuestionDetail] = None
    progress: Optional[ProgressDetail] = None
    feedback: Optional[FeedbackReportDetail] = None
    status: str

class EndInterviewResponse(BaseModel):
    session_id: str
    feedback: FeedbackReportDetail
    status: str = "completed"

class SessionStatusResponse(BaseModel):
    session_id: str
    status: str
    questions_asked: int
    question_budget: int
    days_covered: int
    topics_covered: List[str]
    current_difficulty: str
    current_topic: Optional[str] = None
    difficulty_trajectory: List[str]
    average_score: float

# ── Unified Hackathon API Contract Responses (technical-spec.md) ──
class FeedbackOutput(BaseModel):
    summary: str = Field(..., description="Post-interview overall summary")
    strengths: List[str] = Field(default_factory=list, description="Key candidate strengths")
    gaps: List[str] = Field(default_factory=list, description="Candidate skill gaps")
    next: List[str] = Field(default_factory=list, description="Recommended next steps")
    
    # Optional transparency properties to supply frontend metrics
    overall_score: Optional[float] = None
    hiring_recommendation: Optional[str] = None
    topic_breakdown: Optional[List[Any]] = None
    interview_statistics: Optional[Dict[str, Any]] = None

class UnifiedInterviewResponse(BaseModel):
    reply: str = Field(..., description="Interviewer message/question text")
    done: bool = Field(False, description="Whether interview is finished")
    feedback: Optional[FeedbackOutput] = Field(None, description="Final feedback when done is True")
