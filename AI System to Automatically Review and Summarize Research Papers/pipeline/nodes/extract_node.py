from pathlib import Path
from pipeline.state import PaperState
from pipeline.core.extract import extract_raw_text


def extract_node(state: PaperState) -> PaperState:
    """
    LangGraph node: Extract raw text from PDF.
    """
    pdf_path = Path(state["pdf_path"])
    raw_text = extract_raw_text(pdf_path)

    return {
        "raw_text": raw_text
    }
