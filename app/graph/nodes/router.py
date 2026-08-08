from app.schemas.state import InterviewState
from app.evaluation.difficulty import adjust_difficulty
from app.evaluation.coverage import is_coverage_guaranteed, select_coverage_prioritized_topic
from app.config.settings import settings
from app.utils.logger import logger


def route_decision_node(state: InterviewState) -> InterviewState:
    """
    LangGraph Node: route_decision (Deterministic Router)
    
    Determines the next action: terminate, follow_up, or next_topic.
    For graph edge compatibility, the action is normalized to "terminate" or "continue",
    while the internal routing_decision preserves the granular action type.
    """
    logger.info(f"Executing route_decision_node for session {state['session_id']}")

    q_count = state.get("question_count", 0)
    budget = state.get("question_budget", 8)
    days_covered = state.get("days_covered", [])
    eval_history = state.get("evaluation_history", [])

    latest_eval = eval_history[-1] if eval_history else {}
    latest_score = latest_eval.get("overall_score", 0.5)

    is_followup = state.get("is_followup", False)
    followup_depth = state.get("followup_depth", 0)

    # ── 1. Termination Check ──
    if q_count >= 15:  # Hard ceiling
        action = "terminate"
        reason = "Reached maximum cap of 15 questions."
    elif q_count >= budget and len(days_covered) >= settings.MIN_CURRICULUM_DAYS:
        action = "terminate"
        reason = f"Completed question budget ({q_count}/{budget}) and satisfied coverage ({len(days_covered)} days)."
    elif not is_coverage_guaranteed(len(days_covered), q_count, budget):
        # Coverage at risk — must route to an uncovered day's topic
        action = "next_topic"
        reason = f"Coverage risk ({len(days_covered)}/{settings.MIN_CURRICULUM_DAYS} days). Routing to uncovered day."
    else:
        # Check for second consecutive weak/empty answer
        consecutive_weak_empty = False
        from app.agents.generator_agent import _get_answer_state
        if len(eval_history) >= 2:
            last_score = eval_history[-1].get("overall_score", 0.5)
            prev_score = eval_history[-2].get("overall_score", 0.5)
            
            conv_history = state.get("conversation_history", [])
            cand_answers = [turn["content"] for turn in conv_history if turn["role"] == "candidate"]
            
            if len(cand_answers) >= 2:
                ans_state_1 = _get_answer_state(cand_answers[-1], last_score)
                ans_state_2 = _get_answer_state(cand_answers[-2], prev_score)
                if ans_state_1 in ["WEAK", "EMPTY"] and ans_state_2 in ["WEAK", "EMPTY"]:
                    consecutive_weak_empty = True

        if consecutive_weak_empty:
            action = "next_topic"
            reason = "Second consecutive weak or empty/meaningless answer. Moving to another curriculum topic."
        elif followup_depth < 1 and not is_followup:
            action = "follow_up"
            reason = f"Generating follow-up probe to explore response (score: {latest_score:.2f})."
        else:
            action = "next_topic"
            reason = "Moving to next topic in planned curriculum queue."

    # ── Update state for the next node ──
    if action == "follow_up":
        state["is_followup"] = True
        state["followup_depth"] = followup_depth + 1
        new_difficulty = adjust_difficulty(state, latest_score, is_next_topic=False)
    elif action == "next_topic":
        state["is_followup"] = False
        state["followup_depth"] = 0
        curr_idx = state.get("current_topic_index", 0)
        topic_queue = state.get("topic_queue", [])

        # Prioritize uncovered days if coverage is at risk
        next_idx = select_coverage_prioritized_topic(topic_queue, days_covered, curr_idx)
        state["current_topic_index"] = next_idx

        next_topic_name = topic_queue[next_idx].get("topic") if next_idx < len(topic_queue) else None
        new_difficulty = adjust_difficulty(state, latest_score, is_next_topic=True, next_topic_name=next_topic_name)
    else:  # terminate
        new_difficulty = state.get("current_difficulty", "medium")

    state["current_difficulty"] = new_difficulty
    state["difficulty_trajectory"].append(new_difficulty)

    # Normalize action for graph edge: follow_up and next_topic both map to "continue"
    graph_action = "terminate" if action == "terminate" else "continue"

    state["routing_decision"] = {
        "action": graph_action,        # Used by graph edges: "terminate" | "continue"
        "detailed_action": action,     # Preserved for logging: "terminate" | "follow_up" | "next_topic"
        "reasoning": reason,
        "next_difficulty": new_difficulty
    }

    logger.info(f"Router decision: {action} → graph:{graph_action} | reason: {reason}")
    return state
