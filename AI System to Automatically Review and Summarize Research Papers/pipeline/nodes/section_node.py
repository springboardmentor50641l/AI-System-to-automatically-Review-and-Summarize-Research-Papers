import os
from pipeline.state import PaperState
from pipeline.core.section import semantic_sectioning


def section_node(state: PaperState) -> PaperState:
    api_key = os.getenv("GEMINI_API_KEY")

    try:
        sections = semantic_sectioning(
            state["normalized_text"],
            api_key
        )
    except Exception as e:
        raise ValueError(f"Sectioning failed: {str(e)}")

    return {
        "sections": sections
    }

