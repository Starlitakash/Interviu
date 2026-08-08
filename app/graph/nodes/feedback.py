from app.schemas.state import InterviewState
from app.agents import generate_feedback_agent
from app.utils.logger import logger

def generate_feedback_node(state: InterviewState) -> InterviewState:
    """LangGraph Node: generate_feedback"""
    logger.info(f"Executing generate_feedback_node for session {state['session_id']}")
    
    cand_name = state.get("candidate_profile", {}).get("name", "Candidate")
    eval_history = state.get("evaluation_history", [])
    
    topics = list(state.get("topic_scores", {}).keys())
    if not topics:
        topics = [q.get("topic", "General") for q in state.get("asked_questions", [])]
        
    days = state.get("days_covered", ["Day 1"])
    q_count = state.get("question_count", len(eval_history))
    
    scores = [e.get("overall_score", 0.5) for e in eval_history]
    avg_score = sum(scores) / len(scores) if scores else 0.5
    
    feedback_report = generate_feedback_agent(
        candidate_name=cand_name,
        topics_list=topics,
        days_list=days,
        question_count=q_count,
        avg_score=avg_score,
        evaluation_history=eval_history,
        difficulty_trajectory=state.get("difficulty_trajectory", ["medium"])
    )
    
    fb_dict = {
        "overall_score": feedback_report.overall_score,
        "hiring_recommendation": feedback_report.hiring_recommendation,
        "executive_summary": feedback_report.executive_summary,
        "topic_breakdown": [
            {
                "topic": tb.topic,
                "day": tb.day,
                "score": tb.score,
                "status": tb.status,
                "summary": tb.summary,
                "key_strengths": tb.key_strengths,
                "key_gaps": tb.key_gaps
            }
            for tb in feedback_report.topic_breakdown
        ],
        "strengths": feedback_report.strengths,
        "areas_for_growth": feedback_report.areas_for_growth,
        "actionable_recommendations": feedback_report.actionable_recommendations,
        "interview_statistics": feedback_report.interview_statistics
    }
    
    state["feedback"] = fb_dict
    state["interview_stage"] = "completed"
    
    return state
