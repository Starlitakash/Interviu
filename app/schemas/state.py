from typing import TypedDict, Optional, List, Dict, Set, Any

class InterviewState(TypedDict):
    """LangGraph State definition for Interviu AI Interview Agent"""
    
    # Session Identity
    session_id: str
    interview_stage: str  # planned, in_progress, completed, terminated
    created_at: str
    
    # Input Data
    candidate_profile: Dict[str, Any]
    curriculum: Dict[str, Any]
    tech_spec: str
    
    # Analysis Results
    candidate_analysis: Dict[str, Any]
    
    # Interview Plan
    topic_queue: List[Dict[str, Any]]
    question_budget: int
    current_topic_index: int
    
    # Current Turn
    current_question: Optional[Dict[str, Any]]
    current_answer: Optional[str]
    is_followup: bool
    followup_depth: int
    
    # Tracking
    question_count: int
    asked_questions: List[Dict[str, Any]]
    
    # Evaluation History
    evaluation_history: List[Dict[str, Any]]
    
    # Topic Performance
    topic_scores: Dict[str, List[float]]
    days_covered: List[str]  # Using list for JSON serializability (converted to/from set when computing)
    strong_topics: List[str]
    weak_topics: List[str]
    
    # Difficulty
    current_difficulty: str  # easy, medium_minus, medium, medium_plus, hard
    difficulty_trajectory: List[str]
    consecutive_good: int
    consecutive_bad: int
    
    # Conversation
    conversation_history: List[Dict[str, str]]
    
    # Routing
    routing_decision: Optional[Dict[str, Any]]
    
    # Feedback
    feedback: Optional[Dict[str, Any]]
    
    # Meta
    errors: List[str]
    llm_call_count: int
