from typing import List, Dict, Any, Set
from app.config.settings import settings

def update_days_covered(days_covered_list: List[str], new_day: str) -> List[str]:
    """Idempotently add a curriculum day to days covered list."""
    if not new_day:
        return days_covered_list
    day_str = str(new_day).strip()
    if day_str not in days_covered_list:
        days_covered_list.append(day_str)
    return days_covered_list

def is_coverage_guaranteed(days_covered_count: int, questions_asked: int, question_budget: int) -> bool:
    """Check whether minimum curriculum days constraint is satisfied or strictly reachable."""
    min_days = settings.MIN_CURRICULUM_DAYS
    remaining_questions = question_budget - questions_asked
    days_needed = max(0, min_days - days_covered_count)
    return days_covered_count >= min_days or remaining_questions >= days_needed

def select_coverage_prioritized_topic(
    topic_queue: List[Dict[str, Any]],
    days_covered_list: List[str],
    current_topic_index: int
) -> int:
    """Find the next topic index that introduces an uncovered day if coverage is at risk."""
    days_covered_set = set(days_covered_list)
    
    for idx in range(current_topic_index + 1, len(topic_queue)):
        topic_day = str(topic_queue[idx].get("day", ""))
        if topic_day and topic_day not in days_covered_set:
            return idx
            
    return min(current_topic_index + 1, len(topic_queue) - 1)
