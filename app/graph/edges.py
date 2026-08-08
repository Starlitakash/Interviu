from app.schemas.state import InterviewState

def should_continue(state: InterviewState) -> str:
    """Conditional edge router function."""
    routing = state.get("routing_decision", {})
    if routing.get("action") == "terminate":
        return "terminate"
    return "continue"
