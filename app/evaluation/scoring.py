from typing import List, Dict, Any

def compute_overall_dimension_score(scores: Dict[str, float]) -> float:
    """Weighted average of answer dimension scores."""
    weights = {
        "correctness": 0.30,
        "depth": 0.20,
        "reasoning": 0.20,
        "practical": 0.15,
        "communication": 0.10,
        "completeness": 0.05
    }
    total_score = 0.0
    total_weight = 0.0
    for dim, weight in weights.items():
        val = scores.get(dim, 0.0)
        total_score += val * weight
        total_weight += weight
        
    return round(total_score / total_weight, 2) if total_weight > 0 else 0.0

def update_topic_scores(
    topic_scores: Dict[str, List[float]],
    topic: str,
    score: float
) -> Dict[str, List[float]]:
    """Update topic score list for a specific topic."""
    if topic not in topic_scores:
        topic_scores[topic] = []
    topic_scores[topic].append(score)
    return topic_scores

def classify_topics(topic_scores: Dict[str, List[float]]):
    """Categorize topics into strong (>0.7 avg) and weak (<0.4 avg)."""
    strong = []
    weak = []
    for topic, scores in topic_scores.items():
        if scores:
            avg = sum(scores) / len(scores)
            if avg >= 0.7:
                strong.append(topic)
            elif avg < 0.4:
                weak.append(topic)
    return strong, weak
