from app.schemas.state import InterviewState
from app.agents import generate_question_agent
from app.retrieval import CurriculumIndexer, retrieve_curriculum_context
from app.evaluation.coverage import update_days_covered
from app.utils.logger import logger


def generate_question_node(state: InterviewState, indexer: CurriculumIndexer = None) -> InterviewState:
    """LangGraph Node: generate_question"""
    logger.info(f"Executing generate_question_node for session {state['session_id']}")

    topic_queue = state.get("topic_queue", [])
    curr_idx = state.get("current_topic_index", 0)

    topic_item = {}
    if not topic_queue or curr_idx >= len(topic_queue):
        # Default topic if queue is exhausted
        curr_topic = "System Architecture"
        curr_day = "Day 1"
        logger.warning(f"Topic queue exhausted (idx={curr_idx}, len={len(topic_queue)}). Using default topic.")
    else:
        topic_item = topic_queue[curr_idx]
        curr_topic = topic_item.get("topic", "General Topic")
        curr_day = topic_item.get("day", "Day 1")

    objectives = topic_item.get("objectives") or ["Understand core engineering principles"]
    tools = topic_item.get("tools", [])
    module = topic_item.get("module", {"number": 1, "title": "Environment Setup"})
    reason = topic_item.get("reason", "Standard curriculum selection baseline")

    difficulty = state.get("current_difficulty", "medium")
    q_num = state.get("question_count", 0) + 1
    budget = state.get("question_budget", 8)
    is_followup = state.get("is_followup", False)
    last_answer = state.get("current_answer")

    # Select target turn-specific objective (Step 1 Mapping constraint)
    selected_objective = objectives[(q_num - 1) % len(objectives)]

    # Retrieve RAG context for this topic+day
    rag_content = ""
    if indexer:
        rag_content = retrieve_curriculum_context(indexer, topic=curr_topic, day=curr_day)

    eval_history = state.get("evaluation_history", [])
    latest_score = eval_history[-1].get("overall_score", 0.5) if eval_history else 0.5

    question_model = generate_question_agent(
        topic=curr_topic,
        day=curr_day,
        difficulty=difficulty,
        question_number=q_num,
        total_budget=budget,
        is_followup=is_followup,
        rag_content=rag_content,
        asked_questions=state.get("asked_questions", []),
        conversation_history=state.get("conversation_history", []),
        candidate_profile=state.get("candidate_profile", {}),
        last_answer=last_answer,
        latest_score=latest_score,
        objectives=objectives,
        tools=tools,
        module=module
    )

    # Compile planning trace (Step 4 Rules)
    cand_profile = state.get("candidate_profile", {})
    cand_member = cand_profile.get("member", cand_profile)
    cand_name = cand_member.get("name", "Candidate")
    
    asked_list = state.get("asked_questions", [])
    previous_topics = list(set([q.get("topic") for q in asked_list]))
    remaining_topics = [t.get("topic") for t in topic_queue[curr_idx + 1:]] if topic_queue else []

    trace_dict = {
        "candidate": cand_name,
        "selected_day": curr_day,
        "selected_module": module.get("title", "Module"),
        "selected_topic": curr_topic,
        "selected_objective": selected_objective,
        "reason_selected": reason,
        "difficulty": difficulty,
        "previous_topics": previous_topics,
        "remaining_topics": remaining_topics
    }

    if "planning_traces" not in state:
        state["planning_traces"] = []
    state["planning_traces"].append(trace_dict)

    q_dict = {
        "text": question_model.text,
        "topic": curr_topic,
        "day": curr_day,
        "difficulty": difficulty,
        "question_number": q_num,
        "question_type": question_model.question_type,
        "expected_signals": question_model.expected_signals,
        "context_bridge": question_model.context_bridge,
        "is_followup": is_followup,
        "planning_trace": trace_dict
    }

    state["current_question"] = q_dict
    state["asked_questions"].append(q_dict)
    state["question_count"] = q_num

    # Idempotently update days covered
    state["days_covered"] = update_days_covered(state.get("days_covered", []), curr_day)

    # Build conversational reply with context bridge
    conv_history = state.get("conversation_history", [])
    bridge = question_model.context_bridge or ""
    if bridge and conv_history:
        # Prepend the context bridge to make the question feel connected
        full_message = f"{bridge}\n\n{question_model.text}"
    else:
        full_message = question_model.text

    conv_history.append({
        "role": "interviewer",
        "content": full_message
    })
    state["conversation_history"] = conv_history

    logger.info(f"Generated Q#{q_num}: [{curr_day}] {curr_topic} ({difficulty}) followup={is_followup}")
    return state
