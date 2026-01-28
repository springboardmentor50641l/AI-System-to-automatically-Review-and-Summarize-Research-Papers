import os
from pipeline.state import PaperState
from pipeline.core.section import semantic_sectioning


def section_node(state: PaperState) -> PaperState:
    """
    LangGraph node: Semantic sectioning using Gemini.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    sections = semantic_sectioning(
        state["normalized_text"],
        api_key
    )

    return {
        "sections": sections
    }
