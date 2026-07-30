"""
Assembles the LangGraph StateGraph for the Customer Complaint AI Copilot.

Workflow:

    START -> extract_info -> completeness_check -> duplicate_detection
          -> risk_classification -> root_cause_recommendation
          -> capa_recommendation -> summarize -> END
"""
from langgraph.graph import StateGraph, END

from app.agents.state import ComplaintAgentState
from app.agents import nodes


def build_complaint_graph():
    graph = StateGraph(ComplaintAgentState)

    graph.add_node("extract_info", nodes.extract_info)
    graph.add_node("completeness_check", nodes.completeness_check)
    graph.add_node("duplicate_detection", nodes.duplicate_detection)
    graph.add_node("risk_classification", nodes.risk_classification)
    graph.add_node("root_cause_recommendation", nodes.root_cause_recommendation)
    graph.add_node("recommend_capa", nodes.capa_recommendation)
    graph.add_node("summarize", nodes.summarize)

    graph.set_entry_point("extract_info")
    graph.add_edge("extract_info", "completeness_check")
    graph.add_edge("completeness_check", "duplicate_detection")
    graph.add_edge("duplicate_detection", "risk_classification")
    graph.add_edge("risk_classification", "root_cause_recommendation")
    graph.add_edge("root_cause_recommendation", "recommend_capa")
    graph.add_edge("recommend_capa", "summarize")
    graph.add_edge("summarize", END)

    return graph.compile()


# Compiled once, reused across requests.
complaint_graph = build_complaint_graph()


def run_complaint_workflow(raw_text: str, existing_complaints: list[dict]) -> ComplaintAgentState:
    initial_state: ComplaintAgentState = {
        "raw_text": raw_text,
        "existing_complaints": existing_complaints,
        "errors": [],
    }
    final_state = complaint_graph.invoke(initial_state)
    return final_state
