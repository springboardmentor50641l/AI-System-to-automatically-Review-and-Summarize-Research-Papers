from langgraph.graph import StateGraph, END

from graph.state import PaperState
from graph.nodes import (
    load_node,
    extract_node,
    normalize_node,
    section_node,
    validate_node,
    store_node
)

from graph.review_nodes import (
    aggregate_node,
    key_findings_node,
    comparison_node,
    draft_review_node,
    critique_node,
    revise_node
)


#extraction pipeline

def build_extraction_pipeline():
    graph = StateGraph(PaperState)

    graph.add_node("load", load_node)
    graph.add_node("extract", extract_node)
    graph.add_node("normalize", normalize_node)
    graph.add_node("section", section_node)
    graph.add_node("validate", validate_node)
    graph.add_node("store", store_node)

    graph.set_entry_point("load")

    graph.add_edge("load", "extract")
    graph.add_edge("extract", "normalize")
    graph.add_edge("normalize", "section")
    graph.add_edge("section", "validate")
    graph.add_edge("validate", "store")
    graph.add_edge("store", END)

    return graph.compile()


#review pipeline


def build_review_pipeline():
    graph = StateGraph(PaperState)

    graph.add_node("aggregate", aggregate_node)
    graph.add_node("key_findings", key_findings_node)
    graph.add_node("comparison", comparison_node)
    graph.add_node("draft_review", draft_review_node)
    graph.add_node("critique", critique_node)
    graph.add_node("revise", revise_node)

    graph.set_entry_point("aggregate")

    graph.add_edge("aggregate", "key_findings")
    graph.add_edge("key_findings", "comparison")
    graph.add_edge("comparison", "draft_review")
    graph.add_edge("draft_review", "critique")
    graph.add_edge("critique", "revise")
    graph.add_edge("revise", END)

    return graph.compile()