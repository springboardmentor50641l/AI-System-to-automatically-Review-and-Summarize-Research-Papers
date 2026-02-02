from langgraph.graph import StateGraph
from typing import TypedDict, List

from modules.planner import plan_research
from modules.paper_retrieval import search_papers
from modules.pdf_downloader import download_pdf
from modules.text_extractor import extract_text
from modules.analyzer import analyze_papers
from modules.draft_generator import generate_draft
from modules.reviewer import review_paper

class ResearchState(TypedDict):
    topic: str
    papers: list
    texts: List[str]
    analysis: str
    draft: str
    final: str

def build_workflow():
    graph = StateGraph(ResearchState)

    graph.add_node("planner", plan_research)
    graph.add_node("search", search_papers)
    graph.add_node("extract", extract_text)
    graph.add_node("analyze", analyze_papers)
    graph.add_node("draft", generate_draft)
    graph.add_node("review", review_paper)

    graph.set_entry_point("planner")

    graph.add_edge("planner", "search")
    graph.add_edge("search", "extract")
    graph.add_edge("extract", "analyze")
    graph.add_edge("analyze", "draft")
    graph.add_edge("draft", "review")

    graph.set_finish_point("review")

    return graph.compile()
