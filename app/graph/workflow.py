from langgraph.graph import StateGraph, START, END
from app.schemas.state import InterviewState
from app.graph.nodes import (
    plan_interview_node,
    generate_question_node,
    evaluate_answer_node,
    route_decision_node,
    generate_feedback_node,
)
from app.graph.edges import should_continue
from app.retrieval import CurriculumIndexer

def build_interview_graph(indexer: CurriculumIndexer = None):
    """Build and compile the Interviu LangGraph StateGraph."""
    
    workflow = StateGraph(InterviewState)
    
    # Define node functions with indexer closure if available
    def plan_node_wrapper(state: InterviewState) -> InterviewState:
        return plan_interview_node(state)
        
    def gen_node_wrapper(state: InterviewState) -> InterviewState:
        return generate_question_node(state, indexer=indexer)
        
    def eval_node_wrapper(state: InterviewState) -> InterviewState:
        return evaluate_answer_node(state, indexer=indexer)
        
    def route_node_wrapper(state: InterviewState) -> InterviewState:
        return route_decision_node(state)
        
    def feedback_node_wrapper(state: InterviewState) -> InterviewState:
        return generate_feedback_node(state)

    # Add Nodes
    workflow.add_node("plan_interview", plan_node_wrapper)
    workflow.add_node("generate_question", gen_node_wrapper)
    workflow.add_node("evaluate_answer", eval_node_wrapper)
    workflow.add_node("route_decision", route_node_wrapper)
    workflow.add_node("generate_feedback", feedback_node_wrapper)

    # Add Edges
    workflow.add_edge(START, "plan_interview")
    workflow.add_edge("plan_interview", "generate_question")
    workflow.add_edge("generate_question", END) # Graph pauses for candidate answer
    workflow.add_edge("evaluate_answer", "route_decision")
    
    workflow.add_conditional_edges(
        "route_decision",
        should_continue,
        {
            "continue": "generate_question",
            "terminate": "generate_feedback"
        }
    )
    
    workflow.add_edge("generate_feedback", END)

    return workflow.compile()
