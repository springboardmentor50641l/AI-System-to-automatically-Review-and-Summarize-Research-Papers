from pipeline.state import PaperState
from pipeline.core.normalize import normalize_text


def normalize_node(state: PaperState) -> PaperState:
    """
    LangGraph node: Normalize extracted text.
    """
    raw_text = state["raw_text"]
    normalized_text = normalize_text(raw_text)

    return {
        "normalized_text": normalized_text
    }
