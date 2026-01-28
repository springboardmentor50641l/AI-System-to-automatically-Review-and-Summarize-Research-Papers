from langgraph.graph import StateGraph, END

from pipeline.state import PaperState
from pipeline.nodes.extract_node import extract_node
from pipeline.nodes.normalize_node import normalize_node
from pipeline.nodes.section_node import section_node


def build_graph():
    """
    Build and return the LangGraph pipeline for
    research paper text extraction and sectioning.
    """
    graph = StateGraph(PaperState)

    # Register nodes
    graph.add_node("extract", extract_node)
    graph.add_node("normalize", normalize_node)
    graph.add_node("section", section_node)

    # Define execution order
    graph.set_entry_point("extract")
    graph.add_edge("extract", "normalize")
    graph.add_edge("normalize", "section")
    graph.add_edge("section", END)

    return graph.compile()
