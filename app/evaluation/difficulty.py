from typing import Dict, Any, List
from app.schemas.state import InterviewState

DIFFICULTY_LEVELS = ["very_easy", "easy", "medium", "medium_plus", "hard"]
LEVEL_INDEX = {level: idx for idx, level in enumerate(DIFFICULTY_LEVELS)}

def score_to_difficulty(avg_score: float) -> str:
    """Map average score (0.0-1.0) to a difficulty string level."""
    if avg_score >= 0.85:
        return "hard"
    elif avg_score >= 0.70:
        return "medium_plus"
    elif avg_score >= 0.50:
        return "medium"
    elif avg_score >= 0.30:
        return "easy"
    else:
        return "very_easy"

def adjust_difficulty(state: InterviewState, latest_score: float, is_next_topic: bool = False, next_topic_name: str = None) -> str:
    """
    Consistency-based difficulty adjustment algorithm.
    - Increases difficulty after 2 consecutive good answers (>= 0.7)
    - Decreases difficulty after 1 bad answer (< 0.3)
    - Resets/re-evaluates on topic switch based on prior topic score
    """
    current_difficulty = state.get("current_difficulty", "medium")
    if current_difficulty not in LEVEL_INDEX:
        current_difficulty = "medium"
        
    current_idx = LEVEL_INDEX[current_difficulty]
    consecutive_good = state.get("consecutive_good", 0)
    consecutive_bad = state.get("consecutive_bad", 0)
    
    # Update counters
    if latest_score >= 0.7:
        consecutive_good += 1
        consecutive_bad = 0
    elif latest_score < 0.3:
        consecutive_bad += 1
        consecutive_good = 0
    else:
        consecutive_good = 0
        consecutive_bad = 0

    new_idx = current_idx

    if consecutive_good >= 2:
        new_idx = min(current_idx + 1, len(DIFFICULTY_LEVELS) - 1)
        consecutive_good = 0
    elif consecutive_bad >= 1:
        new_idx = max(current_idx - 1, 0)
        consecutive_bad = 0

    if is_next_topic and next_topic_name:
        topic_scores = state.get("topic_scores", {}).get(next_topic_name, [])
        if topic_scores:
            avg_score = sum(topic_scores) / len(topic_scores)
            new_difficulty = score_to_difficulty(avg_score)
            new_idx = LEVEL_INDEX[new_difficulty]

    # Save state counters back
    state["consecutive_good"] = consecutive_good
    state["consecutive_bad"] = consecutive_bad

    return DIFFICULTY_LEVELS[new_idx]
