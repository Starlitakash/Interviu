from .planner import PLANNER_SYSTEM_PROMPT
from .generator import GENERATOR_SYSTEM_PROMPT
from .evaluator import EVALUATOR_SYSTEM_PROMPT
from .feedback import FEEDBACK_SYSTEM_PROMPT


def format_curriculum_summary(curriculum: dict) -> str:
    """
    Format curriculum JSON into a readable text summary for the planner prompt.
    Handles both nested topics schema and flat days/objectives schema (curriculum.json).
    """
    lines = []

    # Include module-level context if available
    cohort = curriculum.get("cohort", "")
    if cohort:
        lines.append(f"Program: {cohort}")
        lines.append("")

    modules = curriculum.get("modules", [])
    if modules:
        lines.append("Modules:")
        for mod in modules:
            lines.append(f"  Module {mod.get('n', '?')}: {mod.get('title', 'Untitled')} (Days {mod.get('days', [0,0])[0]}-{mod.get('days', [0,0])[-1]})")
        lines.append("")

    for day_obj in curriculum.get("days", []):
        day_num = day_obj.get("day", "?")
        day_title = day_obj.get("title", "Untitled")
        day_type = day_obj.get("type", "LEARNING")
        day_str = f"Day {day_num}: {day_title} [{day_type}]"
        lines.append(day_str)

        # Nested topics schema
        topics = day_obj.get("topics", [])
        if topics:
            for t in topics:
                content_preview = t.get("content", "")[:120]
                lines.append(f"  - {t.get('name', day_title)}: {content_preview}")
        else:
            # Flat schema: tools + objectives (curriculum.json format)
            tools = day_obj.get("tools", [])
            if tools:
                lines.append(f"  Tools: {', '.join(tools)}")
            objectives = day_obj.get("objectives", [])
            for obj in objectives:
                lines.append(f"  • {obj}")

    return "\n".join(lines)


def format_qa_history(conversation_history: list) -> str:
    """Format the last 6 conversation entries for context injection."""
    if not conversation_history:
        return "No conversation history yet — this is the first question."
    formatted = []
    for item in conversation_history[-6:]:
        role = item.get("role", "user")
        content = item.get("content", "")
        label = "Interviewer" if role == "interviewer" else "Candidate"
        formatted.append(f"{label}: {content}")
    return "\n".join(formatted)
