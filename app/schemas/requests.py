from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CurriculumTopic(BaseModel):
    name: str = Field(..., description="Topic name")
    content: str = Field(..., description="Topic content / detailed explanation")
    learning_objectives: List[str] = Field(default_factory=list, description="Objectives")
    key_concepts: List[str] = Field(default_factory=list, description="Key concepts")

class CurriculumDay(BaseModel):
    day: Any = Field(..., description="Day identifier (e.g. 1 or 'Day 1')")
    title: str = Field(..., description="Day title")
    topics: List[CurriculumTopic] = Field(default_factory=list, description="Topics in this curriculum day")

class CurriculumInput(BaseModel):
    days: List[CurriculumDay] = Field(..., description="Curriculum days")

class CandidateProfileInput(BaseModel):
    name: str = Field("Candidate", description="Candidate full name")
    experience_years: float = Field(2, description="Years of experience")
    skills: List[str] = Field(default_factory=list, description="List of technical skills")
    education: Optional[str] = Field(None, description="Educational background")
    projects: List[str] = Field(default_factory=list, description="List of projects")
    current_role: Optional[str] = Field(None, description="Current role title")

class StartInterviewRequest(BaseModel):
    curriculum: Optional[Dict[str, Any]] = Field(None, description="Curriculum specification")
    candidate_profile: Optional[Dict[str, Any]] = Field(None, description="Candidate profile")
    technical_specification: Optional[str] = Field(None, description="Job role technical specification")

class SubmitAnswerRequest(BaseModel):
    session_id: str = Field(..., description="Active interview session UUID")
    answer: str = Field(..., description="Candidate's text response")

class EndInterviewRequest(BaseModel):
    session_id: str = Field(..., description="Active interview session UUID")

# ── Unified Hackathon API Contract (technical-spec.md) ──
class UnifiedInterviewRequest(BaseModel):
    sessionId: str = Field(..., description="Interview Session ID")
    candidate: Optional[Dict[str, Any]] = Field(None, description="Candidate profile JSON (for start turn)")
    message: Optional[str] = Field(None, description="Candidate response text (for continuation turn)")
