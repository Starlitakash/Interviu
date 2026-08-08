import uuid
from datetime import datetime
from typing import Dict, Optional, Tuple
from app.schemas.state import InterviewState
from app.retrieval import CurriculumIndexer
from app.utils.logger import logger

class SessionManager:
    """In-memory Session Store for microsecond state access."""
    
    def __init__(self):
        self._sessions: Dict[str, InterviewState] = {}
        self._indexers: Dict[str, CurriculumIndexer] = {}

    def create_session(
        self,
        candidate_profile: dict,
        curriculum: dict,
        tech_spec: str
    ) -> Tuple[str, InterviewState, CurriculumIndexer]:
        session_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        indexer = CurriculumIndexer(curriculum)
        
        state: InterviewState = {
            "session_id": session_id,
            "interview_stage": "initialized",
            "created_at": created_at,
            "candidate_profile": candidate_profile,
            "curriculum": curriculum,
            "tech_spec": tech_spec,
            "candidate_analysis": {},
            "topic_queue": [],
            "question_budget": 8,
            "current_topic_index": 0,
            "current_question": None,
            "current_answer": None,
            "is_followup": False,
            "followup_depth": 0,
            "question_count": 0,
            "asked_questions": [],
            "evaluation_history": [],
            "topic_scores": {},
            "days_covered": [],
            "strong_topics": [],
            "weak_topics": [],
            "current_difficulty": "medium",
            "difficulty_trajectory": [],
            "consecutive_good": 0,
            "consecutive_bad": 0,
            "conversation_history": [],
            "routing_decision": None,
            "feedback": None,
            "errors": [],
            "llm_call_count": 0
        }
        
        self._sessions[session_id] = state
        self._indexers[session_id] = indexer
        logger.info(f"Session {session_id} created successfully.")
        return session_id, state, indexer

    def get_session(self, session_id: str) -> Optional[Tuple[InterviewState, CurriculumIndexer]]:
        if session_id not in self._sessions:
            return None
        return self._sessions[session_id], self._indexers.get(session_id)

    def update_session(self, session_id: str, state: InterviewState):
        self._sessions[session_id] = state

    def delete_session(self, session_id: str):
        self._sessions.pop(session_id, None)
        self._indexers.pop(session_id, None)

session_manager = SessionManager()
