import json
import os
import traceback
from typing import Tuple, Optional, Dict, Any, List
from app.services.session_manager import session_manager
from app.schemas.state import InterviewState
from app.graph import build_interview_graph
from app.graph.nodes import evaluate_answer_node, route_decision_node, generate_question_node, generate_feedback_node
from app.schemas.requests import StartInterviewRequest, SubmitAnswerRequest, UnifiedInterviewRequest
from app.schemas.responses import (
    StartInterviewResponse,
    SubmitAnswerResponse,
    EndInterviewResponse,
    SessionStatusResponse,
    QuestionDetail,
    InterviewPlanSummary,
    AnswerEvaluationDetail,
    ProgressDetail,
    FeedbackReportDetail,
    DimensionScores,
    UnifiedInterviewResponse,
    FeedbackOutput,
)
from app.utils.logger import logger


def load_default_curriculum() -> Dict[str, Any]:
    """Load default curriculum.json from workspace root."""
    path = os.path.join(os.path.dirname(__file__), "..", "..", "curriculum.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load default curriculum.json: {e}")
    return {"days": []}


def load_default_tech_spec() -> str:
    """Load default technical-spec.md from workspace root."""
    path = os.path.join(os.path.dirname(__file__), "..", "..", "technical-spec.md")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not load default technical-spec.md: {e}")
    return "Technical specification for AI & Software Engineering Role"


class InterviewService:
    """Core Business Service orchestrating LangGraph execution."""

    def start_interview(self, req: StartInterviewRequest) -> StartInterviewResponse:
        curriculum_dict = req.curriculum if req.curriculum else load_default_curriculum()
        profile_dict = req.candidate_profile if req.candidate_profile else {"name": "Candidate", "experience_years": 2}
        tech_spec = req.technical_specification if req.technical_specification else load_default_tech_spec()

        session_id, state, indexer = session_manager.create_session(
            candidate_profile=profile_dict,
            curriculum=curriculum_dict,
            tech_spec=tech_spec
        )

        graph = build_interview_graph(indexer=indexer)
        updated_state = graph.invoke(state)

        session_manager.update_session(session_id, updated_state)

        q_dict = updated_state.get("current_question", {})
        question = QuestionDetail(
            text=q_dict.get("text", "Welcome to your interview!"),
            topic=q_dict.get("topic", "Intro"),
            day=q_dict.get("day", "Day 1"),
            difficulty=q_dict.get("difficulty", "medium"),
            question_number=q_dict.get("question_number", 1),
            question_type=q_dict.get("question_type", "conceptual"),
            is_followup=q_dict.get("is_followup", False),
            context_bridge=q_dict.get("context_bridge")
        )

        topics_planned = [t.get("topic") for t in updated_state.get("topic_queue", [])]
        days_planned = list(set([t.get("day") for t in updated_state.get("topic_queue", [])]))

        plan_summary = InterviewPlanSummary(
            total_questions_planned=updated_state.get("question_budget", 8),
            topics_planned=topics_planned,
            days_planned=days_planned
        )

        return StartInterviewResponse(
            session_id=session_id,
            question=question,
            interview_plan=plan_summary,
            status=updated_state.get("interview_stage", "in_progress")
        )

    def submit_answer(self, req: SubmitAnswerRequest) -> SubmitAnswerResponse:
        session_tuple = session_manager.get_session(req.session_id)
        if not session_tuple:
            raise ValueError(f"Session '{req.session_id}' not found.")

        state, indexer = session_tuple
        if state.get("interview_stage") == "completed":
            raise ValueError(f"Session '{req.session_id}' is already completed.")

        state["current_answer"] = req.answer

        state = evaluate_answer_node(state, indexer=indexer)
        state = route_decision_node(state)

        routing_action = state.get("routing_decision", {}).get("action")

        if routing_action == "terminate":
            state = generate_feedback_node(state)
            session_manager.update_session(req.session_id, state)

            fb = state.get("feedback", {})
            feedback_detail = FeedbackReportDetail(**fb)

            return SubmitAnswerResponse(
                session_id=req.session_id,
                evaluation=self._build_eval_detail(state),
                feedback=feedback_detail,
                status="completed"
            )
        else:
            state = generate_question_node(state, indexer=indexer)
            session_manager.update_session(req.session_id, state)

            q_dict = state.get("current_question", {})
            next_q = QuestionDetail(
                text=q_dict.get("text", ""),
                topic=q_dict.get("topic", ""),
                day=q_dict.get("day", ""),
                difficulty=q_dict.get("difficulty", "medium"),
                question_number=q_dict.get("question_number", 1),
                question_type=q_dict.get("question_type", "conceptual"),
                is_followup=q_dict.get("is_followup", False),
                context_bridge=q_dict.get("context_bridge")
            )

            progress = ProgressDetail(
                questions_asked=state.get("question_count", 1),
                questions_remaining=max(0, state.get("question_budget", 8) - state.get("question_count", 1)),
                topics_covered=list(state.get("topic_scores", {}).keys()),
                days_covered=len(state.get("days_covered", [])),
                current_difficulty=state.get("current_difficulty", "medium")
            )

            return SubmitAnswerResponse(
                session_id=req.session_id,
                evaluation=self._build_eval_detail(state),
                next_question=next_q,
                progress=progress,
                status="in_progress"
            )

    # ── Unified Hackathon Handler for POST /api/interview ──
    def handle_unified_interview(self, req: UnifiedInterviewRequest) -> UnifiedInterviewResponse:
        """
        Single endpoint handler per technical-spec.md.
        - Start turn: sessionId + candidate → first question
        - Continuation: sessionId + message → evaluate + next question or feedback
        """
        session_id = req.sessionId

        try:
            session_tuple = session_manager.get_session(session_id)

            # ── Start Turn (new session or candidate supplied) ──
            if not session_tuple or req.candidate is not None:
                cand_profile = req.candidate if req.candidate else {"name": "Candidate", "experience_years": 2}
                curriculum_dict = load_default_curriculum()
                tech_spec = load_default_tech_spec()

                # Create session using session manager (generates internal UUID)
                internal_id, state, indexer = session_manager.create_session(
                    candidate_profile=cand_profile,
                    curriculum=curriculum_dict,
                    tech_spec=tech_spec
                )

                # Map the user-provided sessionId to the internal session
                # Store under the user's sessionId for consistent lookups
                state["session_id"] = session_id

                graph = build_interview_graph(indexer=indexer)
                updated_state = graph.invoke(state)

                # Persist under the user-provided sessionId
                session_manager.update_session(session_id, updated_state)
                # Also register the indexer under user's sessionId
                session_manager._indexers[session_id] = indexer

                # Build reply with context bridge + question
                q = updated_state.get("current_question", {})
                bridge = q.get("context_bridge", "")
                q_text = q.get("text", "Welcome to your technical interview. Let's begin.")
                reply = f"{bridge}\n\n{q_text}".strip() if bridge else q_text

                logger.info(f"Interview started for session {session_id}")
                return UnifiedInterviewResponse(reply=reply, done=False)

            # ── Continuation Turn ──
            state, indexer = session_tuple

            if state.get("interview_stage") == "completed":
                fb = state.get("feedback", {})
                return UnifiedInterviewResponse(
                    reply="This interview has already been completed. Thank you for your time.",
                    done=True,
                    feedback=FeedbackOutput(
                        summary=fb.get("executive_summary", "Interview evaluation completed."),
                        strengths=fb.get("strengths", []),
                        gaps=fb.get("areas_for_growth", []),
                        next=fb.get("actionable_recommendations", [])
                    )
                )

            message = req.message if req.message else "I'm not sure about that."
            state["current_answer"] = message

            # Evaluate → Route → (Generate next question OR Feedback)
            state = evaluate_answer_node(state, indexer=indexer)
            state = route_decision_node(state)

            routing_action = state.get("routing_decision", {}).get("action")
            detailed_action = state.get("routing_decision", {}).get("detailed_action", routing_action)

            if routing_action == "terminate":
                state = generate_feedback_node(state)
                session_manager.update_session(session_id, state)

                fb = state.get("feedback", {})
                logger.info(f"Interview completed for session {session_id}. Recommendation: {fb.get('hiring_recommendation')}")

                return UnifiedInterviewResponse(
                    reply=fb.get("executive_summary", "Thank you for completing the technical evaluation."),
                    done=True,
                    feedback=FeedbackOutput(
                        summary=fb.get("executive_summary", "Candidate evaluation completed."),
                        strengths=fb.get("strengths", []),
                        gaps=fb.get("areas_for_growth", []),
                        next=fb.get("actionable_recommendations", []),
                        overall_score=fb.get("overall_score"),
                        hiring_recommendation=fb.get("hiring_recommendation"),
                        topic_breakdown=fb.get("topic_breakdown"),
                        interview_statistics=fb.get("interview_statistics")
                    )
                )
            else:
                # Get brief evaluation feedback to include in the reply
                eval_history = state.get("evaluation_history", [])
                latest_eval = eval_history[-1] if eval_history else {}
                eval_feedback = latest_eval.get("brief_feedback", "")

                state = generate_question_node(state, indexer=indexer)
                session_manager.update_session(session_id, state)

                q = state.get("current_question", {})
                bridge = q.get("context_bridge", "")
                q_text = q.get("text", "Can you elaborate on your approach?")

                # Build a conversational reply: evaluation acknowledgment + bridge + question
                parts = []
                if eval_feedback:
                    parts.append(eval_feedback)
                if bridge:
                    parts.append(bridge)
                parts.append(q_text)

                reply = "\n\n".join(parts)

                logger.info(f"Q#{state.get('question_count')} generated ({detailed_action}) for session {session_id}")
                return UnifiedInterviewResponse(reply=reply, done=False)

        except Exception as e:
            logger.error(f"Error in handle_unified_interview: {traceback.format_exc()}")
            return UnifiedInterviewResponse(
                reply=f"I encountered an issue processing your response. Let's continue — could you elaborate on your experience with the current topic?",
                done=False
            )

    def end_interview(self, session_id: str) -> EndInterviewResponse:
        session_tuple = session_manager.get_session(session_id)
        if not session_tuple:
            raise ValueError(f"Session '{session_id}' not found.")

        state, _ = session_tuple
        state = generate_feedback_node(state)
        session_manager.update_session(session_id, state)

        fb = state.get("feedback", {})
        return EndInterviewResponse(
            session_id=session_id,
            feedback=FeedbackReportDetail(**fb),
            status="completed"
        )

    def get_status(self, session_id: str) -> SessionStatusResponse:
        session_tuple = session_manager.get_session(session_id)
        if not session_tuple:
            raise ValueError(f"Session '{session_id}' not found.")

        state, _ = session_tuple
        eval_history = state.get("evaluation_history", [])
        scores = [e.get("overall_score", 0.5) for e in eval_history]
        avg_score = sum(scores) / len(scores) if scores else 0.0

        current_q = state.get("current_question")
        current_topic = current_q.get("topic") if current_q else None

        return SessionStatusResponse(
            session_id=session_id,
            status=state.get("interview_stage", "in_progress"),
            questions_asked=state.get("question_count", 0),
            question_budget=state.get("question_budget", 8),
            days_covered=len(state.get("days_covered", [])),
            topics_covered=list(state.get("topic_scores", {}).keys()),
            current_difficulty=state.get("current_difficulty", "medium"),
            current_topic=current_topic,
            difficulty_trajectory=state.get("difficulty_trajectory", []),
            average_score=round(avg_score, 2)
        )

    def _build_eval_detail(self, state: InterviewState) -> Optional[AnswerEvaluationDetail]:
        eval_history = state.get("evaluation_history", [])
        if not eval_history:
            return None
        latest = eval_history[-1]
        dim_data = latest.get("dimension_scores", {})
        return AnswerEvaluationDetail(
            overall_score=latest.get("overall_score", 0.7),
            dimension_scores=DimensionScores(
                correctness=dim_data.get("correctness", 0.7),
                depth=dim_data.get("depth", 0.7),
                reasoning=dim_data.get("reasoning", 0.7),
                communication=dim_data.get("communication", 0.8),
                practical=dim_data.get("practical", 0.7),
                completeness=dim_data.get("completeness", 0.7),
            ),
            brief_feedback=latest.get("brief_feedback", ""),
            strengths_noted=latest.get("strengths_noted", []),
            areas_to_improve=latest.get("areas_to_improve", [])
        )


interview_service = InterviewService()
