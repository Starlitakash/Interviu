from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class TopicFeedback:
    topic: str
    day: str
    score: float
    status: str  # mastered, satisfactory, needs_work, unassessed
    summary: str
    key_strengths: List[str] = field(default_factory=list)
    key_gaps: List[str] = field(default_factory=list)

@dataclass
class FeedbackReport:
    overall_score: float
    hiring_recommendation: str  # strong_hire, hire, weak_hire, no_hire
    executive_summary: str
    topic_breakdown: List[TopicFeedback] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    areas_for_growth: List[str] = field(default_factory=list)
    actionable_recommendations: List[str] = field(default_factory=list)
    interview_statistics: Dict[str, Any] = field(default_factory=dict)
