import json
import random
from typing import Dict, Any, List, Optional
from app.utils.llm_client import llm_client
from app.prompts import GENERATOR_SYSTEM_PROMPT, format_qa_history
from app.utils.logger import logger
from app.models.question import GeneratedQuestion
from app.agents.planner_agent import normalize_candidate_profile


# Diverse fallback question templates organized by type
FALLBACK_TEMPLATES = {
    "conceptual": [
        "Walk me through the core concepts behind {topic}. What problem does it solve and why is it important in modern systems?",
        "If you had to explain {topic} to a junior engineer, what are the key ideas you'd want them to understand first?",
        "What are the fundamental principles underlying {topic}, and how do they connect to broader software architecture?",
    ],
    "practical": [
        "Can you describe a real-world scenario where you've applied {topic}? What challenges did you face?",
        "If you were building a production system that uses {topic}, what would your implementation approach look like step by step?",
        "What common pitfalls or mistakes do developers make when working with {topic}, and how do you avoid them?",
    ],
    "trade_off": [
        "What are the key trade-offs you'd consider when choosing to use {topic} versus alternative approaches?",
        "How do you decide between different strategies when implementing {topic}? What factors drive that decision in production?",
        "If you had to scale a system using {topic} to handle 100x the current load, what would change in your architecture?",
    ],
    "debugging": [
        "Imagine a system using {topic} starts behaving unexpectedly in production. Walk me through your debugging process.",
        "What are the most common failure modes you've seen with {topic}, and how would you diagnose each one?",
    ],
    "design": [
        "If you were designing a system from scratch that leverages {topic}, what architecture would you propose and why?",
        "How would you integrate {topic} into an existing microservices architecture? What interfaces and contracts would you define?",
    ],
}

FOLLOWUP_TEMPLATES_BY_STATE = {
    "STRONG": [
        "Building on your previous response about {topic}: how would your approach change if you needed to scale concurrent throughput?",
        "You mentioned some interesting points about {topic}. Can you dig deeper into the edge cases in that scenario?",
        "That's a solid foundation. Now let's stress-test your understanding — how would you handle error recovery and fault tolerance in that {topic} setup?",
        "You touched on key aspects of {topic}. Can you elaborate on how you'd monitor and observe this in production?",
    ],
    "PARTIAL": [
        "You explained {topic} partially. Let's dig into the missing parts: how would you address implementation details?",
        "Regarding your response about {topic}: what about the scalability trade-offs you didn't cover?",
        "You touched on some aspects of {topic}, but didn't discuss key design constraints. Can you expand on those?",
    ],
    "WEAK": [
        "Your previous answer was incomplete. Let's approach this {topic} question from another angle: what are the basic requirements?",
        "Let's step back and look at {topic} again. Can you explain the core mechanism in simpler terms?",
        "Since we need more details on {topic}, let's try a simpler focused scenario. How would you start implementing this?",
    ],
    "EMPTY": [
        "Let's try that again. How do you approach the basic concept of {topic}?",
        "I don't think we covered the question about {topic} yet. Let's start with the basic definition.",
        "Let's approach {topic} from a simpler angle. What is the main idea behind it?",
        "Could you explain the basic idea of {topic} first?",
    ]
}


def _get_answer_state(last_answer: Optional[str], latest_score: float) -> str:
    if not last_answer or not last_answer.strip():
        return "EMPTY"
    
    clean_ans = last_answer.lower().strip().strip(".-*").strip()
    if clean_ans in ["ok", "idk", "yes", "no", "hello", "hi", "pass", "i don't know", "i do not know", "meaningless"]:
        return "EMPTY"
        
    if latest_score < 0.15:
        return "EMPTY"
    elif latest_score < 0.40:
        return "WEAK"
    elif latest_score < 0.75:
        return "PARTIAL"
    else:
        return "STRONG"


def _build_rag_fallback_question(topic: str, objectives: List[str], tools: List[str], difficulty: str) -> Optional[str]:
    """
    Build a crisp, curriculum-specific question from objectives list.
    """
    if objectives:
        chosen = random.choice(objectives)
        tool_clause = f" using {random.choice(tools)}" if tools else ""
        templates = [
            f"Regarding {topic}: how do you approach '{chosen}'{tool_clause}?",
            f"Grounding on '{chosen}' in the context of {topic}: walk me through your practical experience and design choices.",
            f"Let's focus on a specific aspect of {topic}: '{chosen}'. What are the primary trade-offs you consider here?",
        ]
        return random.choice(templates)
    return None


def _get_default_signals(topic: str, selected_objective: str, tools: list) -> list:
    signals = []
    if selected_objective:
        signals.append(selected_objective)
    if topic:
        signals.append(topic)
        for word in topic.replace("&", " ").replace("-", " ").split():
            word_clean = word.strip().lower()
            if len(word_clean) > 2 and word_clean not in ["and", "the", "for", "with"]:
                signals.append(word)
    if tools:
        signals.extend(tools)
    return list(set(signals))


def generate_question_agent(
    topic: str,
    day: str,
    difficulty: str,
    question_number: int,
    total_budget: int,
    is_followup: bool,
    rag_content: str,
    asked_questions: List[Dict[str, Any]],
    conversation_history: List[Dict[str, str]],
    candidate_profile: Dict[str, Any],
    last_answer: Optional[str] = None,
    latest_score: float = 0.5,
    objectives: List[str] = None,
    tools: List[str] = None,
    module: Dict[str, Any] = None
) -> GeneratedQuestion:
    """
    Run Generator Agent to produce the next interview question.
    Ensures strict mapping: 1 day -> 1 objective -> 1 question.
    """
    norm_profile = normalize_candidate_profile(candidate_profile)
    job_role = norm_profile.get("jobRole", "Developer")
    experience_years = norm_profile.get("experience_years", 2)
    name = norm_profile.get("name", "Candidate")

    asked_str = "\n".join([f"- [{q.get('day')}] {q.get('topic')}: {q.get('text')}" for q in asked_questions]) if asked_questions else "None"
    qa_history_str = format_qa_history(conversation_history)

    # Automatically choose one specific objective to focus on for this turn
    objectives = objectives or ["General engineering principles"]
    tools = tools or []
    
    # Simple deterministic index matching turn context
    obj_idx = (question_number - 1) % len(objectives)
    selected_objective = objectives[obj_idx]

    followup_ctx = ""
    if is_followup:
        last_ans_text = last_answer or ""
        ans_state = _get_answer_state(last_ans_text, latest_score)
        if ans_state == "STRONG":
            followup_ctx = (
                f"CANDIDATE'S PREVIOUS ANSWER (STRONG performance, score {latest_score}):\n"
                f"<last_answer>\n{last_ans_text}\n</last_answer>\n"
                f"INSTRUCTION: Candidate gave a STRONG response. Ask a deeper implementation or scenario follow-up question. "
                f"You may use transition phrases like 'Building on your previous response...' or 'You mentioned [X]. Let's explore...', "
                f"BUT ONLY if the candidate actually demonstrated the referenced concept. Do NOT hallucinate concepts they did not mention."
            )
            question_type = "practical"
        elif ans_state == "PARTIAL":
            followup_ctx = (
                f"CANDIDATE'S PREVIOUS ANSWER (PARTIAL performance, score {latest_score}):\n"
                f"<last_answer>\n{last_ans_text}\n</last_answer>\n"
                f"INSTRUCTION: Candidate answered PARTIALLY. Target the missing concepts related to '{selected_objective}'. "
                f"Formulate the follow-up explicitly targeting the missing concept. "
                f"Example transition wording: 'You mentioned [X], but didn't discuss [Y]. How would you handle [Y]?'"
            )
            question_type = "practical"
        elif ans_state == "WEAK":
            followup_ctx = (
                f"CANDIDATE'S PREVIOUS ANSWER (WEAK performance, score {latest_score}):\n"
                f"<last_answer>\n{last_ans_text}\n</last_answer>\n"
                f"INSTRUCTION: Candidate gave a WEAK response. Do NOT claim the candidate made interesting points or has a solid foundation. "
                f"Use transition wording: 'Your previous answer was incomplete. Let's approach this from another angle.' "
                f"Then ask a simpler, more focused question about '{selected_objective}'."
            )
            question_type = "conceptual"
        else: # EMPTY
            followup_ctx = (
                f"CANDIDATE'S PREVIOUS ANSWER: '{last_ans_text}' (EMPTY / MEANINGLESS / ZERO DETECTED CONCEPTS).\n"
                f"INSTRUCTION: Candidate gave an empty, meaningless, or zero-concept answer. "
                f"NEVER use phrases like 'Building on your previous response', 'You mentioned', 'That's a solid foundation', "
                f"'You touched on', or 'Interesting points'. "
                f"Instead, use natural recovery language such as: 'Let's try that again', 'I don't think we covered the question yet', "
                f"'Let's approach it from a simpler angle', or 'Could you explain the basic idea first?'. "
                f"Then generate a simpler question related to the same learning objective ('{selected_objective}')."
            )
            question_type = "conceptual"
    else:
        question_type = "practical" if is_followup else ("conceptual" if difficulty in ["easy", "very_easy"] else "trade_off")

    # Step 9: Wording influence based on Job Role
    role_instruction = ""
    jr_lower = job_role.lower()
    if "business analyst" in jr_lower or "analyst" in jr_lower:
        role_instruction = (
            "IMPORTANT: The candidate is a Business Analyst. Do NOT ask deeply technical syntax or code details. "
            "Instead, ask conceptual questions focusing on AI adoption, product trade-offs, and operational utility "
            "of the topic, keeping it strictly based on the provided curriculum content."
        )
    elif "data engineer" in jr_lower or "data" in jr_lower:
        role_instruction = (
            "IMPORTANT: The candidate is a Senior Data Engineer. Wording should focus on data pipelines, performance at scale, "
            "database architecture, and data flow of the topic."
        )
    else:
        role_instruction = (
            "IMPORTANT: The candidate is a Software Engineer / Developer. Focus the question on implementation details, API design, "
            "code structure, and error handling of the topic."
        )

    # Curriculum mapping instructions to satisfy BUG 1, 6, and 7
    curriculum_instructions = f"""
CURRICULUM MAPPING AND INTEGRITY CONSTRAINTS:
- You must generate a question ONLY for the topic "{topic}" (from {day}).
- The target learning objective for this turn is: "{selected_objective}".
- Ground the generated question ENTIRELY on this single objective. Do NOT mix multiple objectives or bring in topics from other days.
- The question must be short and crisp: MAXIMUM 2-3 sentences.
- Focus on one core concept and one follow-up point. Do NOT ask multiple unrelated questions in a single turn.
"""

    custom_instruction = f"""
CANDIDATE PROFILE:
- Name: {name}
- Target Role: {job_role}
- Experience: {experience_years} years
- Education: {norm_profile.get("education")}

ROLE SPECIFIC WORDING INSTRUCTION:
{role_instruction}

{curriculum_instructions}
"""

    prompt = GENERATOR_SYSTEM_PROMPT.format(
        topic=topic,
        day=day,
        difficulty=difficulty,
        question_number=question_number,
        total_budget=total_budget,
        is_followup=is_followup,
        rag_retrieved_content=rag_content,
        last_3_qa_pairs=qa_history_str,
        asked_questions_list=asked_str,
        followup_context=followup_ctx + "\n" + custom_instruction,
        question_type=question_type
    )

    text_res = llm_client.generate(prompt, temperature=0.7)
    parsed = None
    if text_res:
        from app.utils.output_parser import parse_json_from_llm_text
        parsed = parse_json_from_llm_text(text_res)

    if parsed and "text" in parsed:
        logger.info(f"[OK] Generator produced LLM question for {topic} ({day}) - Obj: {selected_objective}")
        
        bridge = parsed.get("context_bridge", f"Let's explore {topic}.")
        ans_state = _get_answer_state(last_answer, latest_score) if is_followup else "STRONG"
        if is_followup:
            if ans_state == "EMPTY":
                bridge = random.choice([
                    "Let's try that again.",
                    "I don't think we covered the question yet.",
                    "Let's approach it from a simpler angle.",
                    "Could you explain the basic idea first?"
                ])
            elif ans_state == "WEAK":
                bridge = "Your previous answer was incomplete. Let's approach this from another angle."

        return GeneratedQuestion(
            text=parsed.get("text"),
            topic=topic,
            day=day,
            difficulty=difficulty,
            question_type=parsed.get("question_type", question_type),
            expected_signals=parsed.get("expected_signals", _get_default_signals(topic, selected_objective, tools)),
            context_bridge=bridge,
            is_followup=is_followup
        )

    # Fallback options
    logger.info(f"[WARN] Generator using fallback for {topic} ({day})")

    if is_followup:
        ans_state = _get_answer_state(last_answer, latest_score)
        templates = FOLLOWUP_TEMPLATES_BY_STATE.get(ans_state, FOLLOWUP_TEMPLATES_BY_STATE["STRONG"])
        q_text = random.choice(templates).format(topic=topic)
        
        if ans_state == "EMPTY":
            bridge = "Let's try that again."
        elif ans_state == "WEAK":
            bridge = "Your previous answer was incomplete. Let's approach this from another angle."
        elif ans_state == "PARTIAL":
            bridge = f"You touched on some aspects of {topic}, but let's look at the remaining details."
        else:
            bridge = f"Building on your previous response about {topic}..."
    else:
        rag_question = _build_rag_fallback_question(topic, objectives, tools, difficulty)
        if rag_question:
            q_text = rag_question
        else:
            templates = FALLBACK_TEMPLATES.get(question_type, FALLBACK_TEMPLATES["conceptual"])
            q_text = random.choice(templates).format(topic=topic)
        bridge = f"Moving to our next topic: {topic}."

    return GeneratedQuestion(
        text=q_text,
        topic=topic,
        day=day,
        difficulty=difficulty,
        question_type=question_type,
        expected_signals=_get_default_signals(topic, selected_objective, tools),
        context_bridge=bridge,
        is_followup=is_followup
    )
