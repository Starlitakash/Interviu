from typing import Dict, Any, List, Optional
from app.utils.llm_client import llm_client
from app.prompts import EVALUATOR_SYSTEM_PROMPT
from app.utils.logger import logger
from app.models.evaluation import AnswerEvaluation, DimensionScoresModel


def _heuristic_evaluate(candidate_answer: str, expected_signals: List[str], question_text: str) -> AnswerEvaluation:
    """
    Improved heuristic evaluator that checks for signal keyword matches,
    answer structure, and depth indicators.
    """
    ans_lower = candidate_answer.lower()
    words = candidate_answer.split()
    word_count = len(words)

    # Signal Detection with smart suffix, prefix, and clean-verb matching
    signals_hit = []
    stop_verbs = {
        "understand", "know", "build", "implement", "learn", "discuss",
        "analyze", "explain", "design", "write", "the", "a", "an",
        "of", "to", "in", "for", "with", "and", "or", "about"
    }

    for signal in expected_signals:
        signal_lower = signal.lower()
        signal_words = signal_lower.split()
        
        if len(signal_words) == 1:
            word = signal_words[0]
            if word in ans_lower:
                signals_hit.append(signal)
            else:
                # Check prefix/suffix overlaps for plurals, gerunds, etc.
                matched = False
                for w in ans_lower.replace(".", " ").replace(",", " ").split():
                    if len(w) >= 3 and len(word) >= 3:
                        if w.startswith(word) or word.startswith(w):
                            matched = True
                            break
                if matched:
                    signals_hit.append(signal)
        else:
            # Multi-word signals: filter stop words/verbs and check overlap
            sig_clean_words = [w for w in signal_words if w not in stop_verbs]
            if not sig_clean_words:
                sig_clean_words = signal_words
                
            hit_count = 0
            for sw in sig_clean_words:
                if sw in ans_lower:
                    hit_count += 1
                else:
                    for w in ans_lower.replace(".", " ").replace(",", " ").split():
                        if len(w) >= 3 and len(sw) >= 3:
                            if w.startswith(sw) or sw.startswith(w):
                                hit_count += 1
                                break
            if hit_count >= len(sig_clean_words) * 0.5:
                signals_hit.append(signal)

    signal_ratio = len(signals_hit) / max(len(expected_signals), 1)

    # Depth Indicators
    depth_markers = ["because", "therefore", "for example", "in practice", "the reason",
                     "trade-off", "tradeoff", "however", "although", "specifically",
                     "for instance", "this means", "as a result", "in production",
                     "the advantage", "the disadvantage", "compared to", "unlike"]
    depth_count = sum(1 for marker in depth_markers if marker in ans_lower)

    # Structure Indicators
    has_examples = any(m in ans_lower for m in ["for example", "for instance", "such as", "e.g.", "like when"])
    has_reasoning = any(m in ans_lower for m in ["because", "since", "the reason", "this is due to", "therefore"])
    uses_technical_terms = word_count > 5 and any(len(w) > 8 for w in words)

    # Base length scores
    if word_count >= 80:
        length_score = 0.85
    elif word_count >= 40:
        length_score = 0.7
    elif word_count >= 20:
        length_score = 0.55
    elif word_count >= 8:
        length_score = 0.35
    else:
        length_score = 0.15

    # Relax length score for high-information density
    if signal_ratio >= 0.8:
        length_score = max(length_score, 0.9)
    elif signal_ratio >= 0.6:
        length_score = max(length_score, 0.75)
    elif signal_ratio >= 0.4:
        length_score = max(length_score, 0.6)

    # Scoring with relaxed length penalty for high-information density
    penalty = 1.0
    if word_count < 10:
        penalty = 0.35
    elif word_count < 20:
        penalty = 0.7
    elif word_count < 40:
        penalty = 0.85

    if not signals_hit:
        penalty *= 0.2

    boost = 0.0
    if signal_ratio >= 0.8:
        boost = 0.55
        penalty = max(penalty, 0.98)
    elif signal_ratio >= 0.6:
        boost = 0.45
        penalty = max(penalty, 0.92)
    elif signal_ratio >= 0.4:
        boost = 0.35
        penalty = max(penalty, 0.85)

    correctness = min(1.0, length_score * 0.5 + signal_ratio * 0.5 + boost) * penalty
    depth = min(1.0, 0.1 + depth_count * 0.1 + (0.15 if has_examples else 0) + (0.1 if has_reasoning else 0) + boost * 1.5) * penalty
    reasoning = min(1.0, 0.1 + (0.3 if has_reasoning else 0) + depth_count * 0.08 + boost * 1.5) * penalty
    communication = min(1.0, 0.2 + (0.2 if word_count > 15 else 0) + (0.1 if "." in candidate_answer else 0) + boost) * penalty
    practical = min(1.0, 0.1 + (0.3 if has_examples else 0) + (0.2 if uses_technical_terms else 0) + boost) * penalty
    completeness = min(1.0, signal_ratio * 0.7 + length_score * 0.3 + boost) * penalty

    overall = round(
        correctness * 0.30 + depth * 0.20 + reasoning * 0.20 +
        practical * 0.15 + communication * 0.10 + completeness * 0.05,
        2
    )
    overall = min(0.95, overall)

    strengths = []
    areas = []
    if signal_ratio > 0.5:
        strengths.append(f"Addressed {len(signals_hit)}/{len(expected_signals)} expected technical concepts")
    if has_examples:
        strengths.append("Provided concrete examples to support explanation")
    if has_reasoning:
        strengths.append("Showed clear reasoning and causal thinking")
    if depth_count >= 2:
        strengths.append("Demonstrated analytical depth")
    if not strengths:
        strengths.append("Attempted to address the question")

    if signal_ratio < 0.5:
        areas.append(f"Cover more expected concepts ({len(expected_signals) - len(signals_hit)} missed)")
    if not has_examples:
        areas.append("Include practical examples or real-world scenarios")
    if not has_reasoning:
        areas.append("Explain the 'why' behind your technical choices")
    if word_count < 30:
        areas.append("Provide more detailed and thorough responses")

    feedback = f"Score: {overall:.0%}. " + (
        f"Strong coverage of {len(signals_hit)} signals with good depth."
        if overall >= 0.7 else
        f"Partial coverage — {len(signals_hit)}/{len(expected_signals)} signals detected. More depth needed."
        if overall >= 0.4 else
        "Very brief response. Try to elaborate with specifics and examples."
    )

    dims = DimensionScoresModel(
        correctness=correctness, depth=depth, reasoning=reasoning,
        communication=communication, practical=practical, completeness=completeness
    )
    return AnswerEvaluation(
        overall_score=overall,
        dimension_scores=dims,
        brief_feedback=feedback,
        strengths_noted=strengths,
        areas_to_improve=areas,
        signals_detected=signals_hit
    )


def evaluate_answer_agent(
    question_text: str,
    expected_signals: list,
    candidate_answer: str,
    rag_content: str,
    rubric: str = ""
) -> AnswerEvaluation:
    """
    Run Evaluator Agent on candidate's answer.
    Step 2: Uses semantic LLM evaluation against derived curriculum rubrics.
    """

    # Pre-check edge cases: Empty, IDK, or extremely short meaningless answers
    ans_clean = (candidate_answer or "").strip().lower()
    meaningless_answers = {
        "ok", "yes", "no", "hello", "hi", "okay", "thanks", "thank you",
        "idk", "i don't know", "no idea", "i do not know", "pass", "skip",
        "i'm not sure", "not sure", "sure", "yep", "yup", "fine", "hello there",
        "none", "na", "n/a", "nothing", "next", "dunno", "no clue"
    }
    word_count = len(ans_clean.split())
    has_signals = any(sig.lower() in ans_clean for sig in expected_signals) if expected_signals else False
    
    is_meaningless = (
        ans_clean in meaningless_answers or
        word_count == 0 or
        (word_count < 4 and not has_signals)
    )

    if is_meaningless:
        logger.info(f"Evaluator detected empty/meaningless/IDK answer: '{candidate_answer}'")
        return AnswerEvaluation(
            overall_score=0.05,
            dimension_scores=DimensionScoresModel(
                correctness=0.0, depth=0.0, reasoning=0.0,
                communication=0.1, practical=0.0, completeness=0.0
            ),
            brief_feedback="Candidate provided a very short, empty, or meaningless response that does not address the question.",
            strengths_noted=[],
            areas_to_improve=["Provide a complete, technically detailed answer."],
            signals_detected=[],
            is_empty_or_idk=True
        )

    signals_str = ", ".join(expected_signals) if expected_signals else "Core technical concepts"

    # Invert/inject semantic instructions and rubric
    semantic_instructions = f"""
EVALUATION RUBRIC FOR THIS SYLLABUS TOPIC:
{rubric}

ADDITIONAL EVALUATION INSTRUCTIONS:
- You MUST perform semantic evaluation. Never score based on exact keyword matching. Recognize and award full credit for equivalent conceptual explanations or alternate phrasing (e.g. if the candidate describes Reciprocal Rank Fusion or latency trade-offs without using those exact words, mark it as correct).
- Compare the answer against the provided syllabus curriculum reference.
- Return structured scores and constructive evidence-based strengths/weaknesses referencing the candidate's actual answer content.
- In the output JSON, you MUST include the following keys:
  "confidence": "high|medium|low",
  "practical_depth": "basic|intermediate|advanced|expert",
  "suggested_followup": "a constructive follow-up question targeting candidate gaps or pushing implementation details",
  "concepts_covered": ["concept 1", "concept 2"],
  "concepts_missing": ["concept 3", "concept 4"]
"""

    prompt = EVALUATOR_SYSTEM_PROMPT.format(
        question_text=question_text,
        expected_signals=signals_str + "\n" + semantic_instructions,
        candidate_answer=candidate_answer,
        rag_retrieved_content=rag_content
    )

    text_res = llm_client.generate(prompt, temperature=0.2)
    parsed = None
    if text_res:
        from app.utils.output_parser import parse_json_from_llm_text
        parsed = parse_json_from_llm_text(text_res)

    if parsed and "overall_score" in parsed:
        logger.info(f"[OK] Evaluator produced LLM evaluation (score: {parsed.get('overall_score')})")
        dim_data = parsed.get("dimension_scores", {})
        dims = DimensionScoresModel(
            correctness=float(dim_data.get("correctness", 0.7)),
            depth=float(dim_data.get("depth", 0.7)),
            reasoning=float(dim_data.get("reasoning", 0.7)),
            communication=float(dim_data.get("communication", 0.8)),
            practical=float(dim_data.get("practical", 0.7)),
            completeness=float(dim_data.get("completeness", 0.7))
        )
        
        # Convert overall score out of 10 to a 0.0-1.0 float if necessary
        raw_score = float(parsed.get("overall_score", 0.7))
        score = raw_score / 10.0 if raw_score > 1.0 else raw_score
        
        return AnswerEvaluation(
            overall_score=score,
            dimension_scores=dims,
            brief_feedback=parsed.get("brief_feedback", "Solid technical answer."),
            strengths_noted=parsed.get("strengths_noted", ["Accurate concept explanation"]),
            areas_to_improve=parsed.get("areas_to_improve", ["Could provide deeper practical example"]),
            signals_detected=parsed.get("signals_detected", expected_signals),
            is_off_topic=parsed.get("is_off_topic", False),
            is_empty_or_idk=parsed.get("is_empty_or_idk", False),
            confidence=parsed.get("confidence", "medium"),
            practical_depth=parsed.get("practical_depth", "medium"),
            suggested_followup=parsed.get("suggested_followup", ""),
            concepts_covered=parsed.get("concepts_covered", []),
            concepts_missing=parsed.get("concepts_missing", [])
        )

    # Fallback Option
    logger.info("[WARN] Evaluator using signal-aware heuristic fallback.")
    return _heuristic_evaluate(candidate_answer, expected_signals, question_text)
