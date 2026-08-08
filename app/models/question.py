from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class GeneratedQuestion:
    text: str
    topic: str
    day: str
    difficulty: str
    question_type: str  # conceptual, practical, edge_case, code_reading
    expected_signals: List[str] = field(default_factory=list)
    context_bridge: Optional[str] = None
    is_followup: bool = False
    followup_depth: int = 0
