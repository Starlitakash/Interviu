from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class TopicPlanItem:
    day: str
    topic: str
    priority: str  # high, medium, low
    allocated_questions: int
    status: str = "pending"  # pending, in_progress, completed

@dataclass
class CandidateAnalysis:
    strengths: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    experience_level: str = "mid"  # junior, mid, senior
    priority_topics: List[str] = field(default_factory=list)
    reasoning: str = ""
