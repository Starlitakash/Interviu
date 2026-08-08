from app.schemas.state import InterviewState
from app.agents import evaluate_answer_agent
from app.retrieval import CurriculumIndexer, retrieve_curriculum_context
from app.evaluation.scoring import update_topic_scores, classify_topics
from app.utils.logger import logger

def evaluate_answer_node(state: InterviewState, indexer: CurriculumIndexer = None) -> InterviewState:
    """LangGraph Node: evaluate_answer"""
    logger.info(f"Executing evaluate_answer_node for session {state['session_id']}")
    
    current_q = state.get("current_question", {})
    candidate_answer = state.get("current_answer", "")
    
    q_text = current_q.get("text", "Technical Question")
    signals = current_q.get("expected_signals", [])
    topic = current_q.get("topic", "General Topic")
    day = current_q.get("day", "Day 1")
    
    # Save candidate response to conversation history
    state["conversation_history"].append({
        "role": "candidate",
        "content": candidate_answer
    })
    
    # Retrieve RAG content for evaluation ground truth
    rag_content = ""
    if indexer:
        rag_content = retrieve_curriculum_context(indexer, topic=topic, day=day)

    # Automatically derive rubric from curriculum.json day data (Step 8)
    curriculum = state.get("curriculum", {})
    day_num = 1
    try:
        day_num = int(day.replace("Day", "").strip())
    except Exception:
        pass
    
    day_data = {}
    for d_obj in curriculum.get("days", []):
        if int(d_obj.get("day", 0)) == day_num:
            day_data = d_obj
            break

    topic_title = day_data.get("title", topic)
    objectives = day_data.get("objectives", [])
    tools = day_data.get("tools", [])
    
    expected_concepts = [f"Understand core principles of {topic_title}"] + objectives[:2]
    expected_examples = [f"Practical implementation of {tool}" for tool in tools[:2]] if tools else [f"Scenario applying {topic_title}"]
    expected_production = [f"Best practices, scalability, or error handling with {topic_title}"]
    expected_tradeoffs = [f"Trade-offs, performance costs, or comparative analysis of {topic_title}"]
    expected_practical = [f"Hands-on configuration, usage, or debugging of {topic_title}"]
    
    derived_rubric = f"""EVALUATION RUBRIC FOR: {topic_title}
1. EXPECTED CONCEPTS:
{chr(10).join([f"   - {c}" for c in expected_concepts])}
2. EXPECTED EXAMPLES:
{chr(10).join([f"   - {e}" for e in expected_examples])}
3. EXPECTED PRODUCTION KNOWLEDGE:
{chr(10).join([f"   - {p}" for p in expected_production])}
4. EXPECTED TRADEOFFS:
{chr(10).join([f"   - {t}" for t in expected_tradeoffs])}
5. EXPECTED PRACTICAL EXPERIENCE:
{chr(10).join([f"   - {pr}" for pr in expected_practical])}
"""

    eval_result = evaluate_answer_agent(
        question_text=q_text,
        expected_signals=signals,
        candidate_answer=candidate_answer,
        rag_content=rag_content,
        rubric=derived_rubric
    )
    
    # Extract objective from trace
    trace = current_q.get("planning_trace") or {}
    selected_objective = trace.get("selected_objective", "Understand core principles")

    eval_dict = {
        "question": current_q,
        "answer": candidate_answer,
        "overall_score": eval_result.overall_score,
        "dimension_scores": {
            "correctness": eval_result.dimension_scores.correctness,
            "depth": eval_result.dimension_scores.depth,
            "reasoning": eval_result.dimension_scores.reasoning,
            "communication": eval_result.dimension_scores.communication,
            "practical": eval_result.dimension_scores.practical,
            "completeness": eval_result.dimension_scores.completeness,
        },
        "brief_feedback": eval_result.brief_feedback,
        "strengths_noted": eval_result.strengths_noted,
        "areas_to_improve": eval_result.areas_to_improve,
        "signals_detected": eval_result.signals_detected,
        "is_off_topic": eval_result.is_off_topic,
        "is_empty_or_idk": eval_result.is_empty_or_idk,
        
        # Memory specifications (Step 1 Memory requirement)
        "curriculum_day": day,
        "topic": topic,
        "learning_objective": selected_objective,
        "answer_score": int(eval_result.overall_score * 100),
        "confidence": eval_result.confidence or "medium",
        "demonstrated_concepts": eval_result.concepts_covered or [f"Understands {topic}"],
        "missing_concepts": eval_result.concepts_missing or [],
        "strengths": eval_result.strengths_noted or ["Answered the question"],
        "weaknesses": eval_result.areas_to_improve or [],
        "follow_up_reason": eval_result.suggested_followup or "Explore concept parameters"
    }
    
    state["evaluation_history"].append(eval_dict)
    
    # Update topic scores and classify
    topic_scores = update_topic_scores(state.get("topic_scores", {}), topic, eval_result.overall_score)
    state["topic_scores"] = topic_scores
    
    strong, weak = classify_topics(topic_scores)
    state["strong_topics"] = strong
    state["weak_topics"] = weak
    
    return state
