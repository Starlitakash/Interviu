from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class DimensionScoresModel:
    correctness: float = 0.0
    depth: float = 0.0
    reasoning: float = 0.0
    communication: float = 0.0
    practical: float = 0.0
    completeness: float = 0.0


@dataclass
class AnswerEvaluation:
    overall_score: float
    dimension_scores: DimensionScoresModel
    brief_feedback: str
    strengths_noted: List[str] = field(default_factory=list)
    areas_to_improve: List[str] = field(default_factory=list)
    signals_detected: List[str] = field(default_factory=list)
    is_off_topic: bool = False
    is_empty_or_idk: bool = False
    confidence: str = "medium"
    practical_depth: str = "medium"
    suggested_followup: str = ""
    concepts_covered: List[str] = field(default_factory=list)
    concepts_missing: List[str] = field(default_factory=list)
