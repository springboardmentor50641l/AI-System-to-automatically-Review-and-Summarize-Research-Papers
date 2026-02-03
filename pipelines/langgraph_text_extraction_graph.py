
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from pipelines.langgraph_text_extraction_nodes import(PaperState,empty_sections, load_paper_node,extract_text_node, normalize_text_node,semantic_sectioning_node, validate_sections_node, store_sections_node,extract_key_findings,compare_papers,generate_draft)

graph = StateGraph(PaperState)

# Nodes
graph.add_node("load", load_paper_node)
graph.add_node("extract", extract_text_node)
graph.add_node("normalize", normalize_text_node)
graph.add_node("section", semantic_sectioning_node)
graph.add_node("validate", validate_sections_node)
graph.add_node("store", store_sections_node)
graph.add_node("key_findings", extract_key_findings_node)  # NEW

# Entry
graph.set_entry_point("load")

# Edges
graph.add_edge("load", "extract")
graph.add_edge("extract", "normalize")
graph.add_edge("normalize", "section")
graph.add_edge("section", "validate")
graph.add_edge("validate", "store")
graph.add_edge("store","key_findings")
graph.add_edge("key_findings", END)

pipeline = graph.compile()




if __name__ == "__main__":
    result = pipeline.invoke({"pdf_path": r"text_extraction\sample_paper\test_paper.pdf"})
    print(result["sections"])