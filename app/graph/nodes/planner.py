from app.schemas.state import InterviewState
from app.agents import plan_interview_agent
from app.retrieval import CurriculumIndexer
from app.utils.logger import logger

def plan_interview_node(state: InterviewState) -> InterviewState:
    """LangGraph Node: plan_interview"""
    logger.info(f"Executing plan_interview_node for session {state['session_id']}")
    
    cand_profile = state.get("candidate_profile", {})
    curriculum = state.get("curriculum", {})
    tech_spec = state.get("tech_spec", "")
    
    analysis, topic_queue, starting_diff, budget = plan_interview_agent(
        candidate_profile=cand_profile,
        curriculum=curriculum,
        tech_spec=tech_spec
    )
    
    state["candidate_analysis"] = analysis
    state["topic_queue"] = topic_queue
    state["question_budget"] = budget
    state["current_difficulty"] = starting_diff
    state["difficulty_trajectory"] = [starting_diff]
    state["interview_stage"] = "in_progress"
    
    return state
