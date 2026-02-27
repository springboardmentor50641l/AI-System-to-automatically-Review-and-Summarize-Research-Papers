import fitz 
from typing import TypedDict, Optional, Dict, Any


#state definition

class GraphState(TypedDict, total=False):
    pdf_path: str
    paper_text: str
    error: Optional[str]


def text_extraction_node(state: GraphState) -> Dict[str, Any]:
    """
    LangGraph Node:
    Extracts text from a given PDF file path
    and updates the graph state.
    """

    pdf_path = state.get("pdf_path")

    if not pdf_path:
        return {"error": "No PDF path provided in state."}

    try:
        extracted_text = ""

        with fitz.open(pdf_path) as doc:
            for page in doc:
                extracted_text += page.get_text()

        if not extracted_text.strip():
            return {"error": "PDF text extraction returned empty content."}

        return {
            "paper_text": extracted_text
        }

    except Exception as e:
        return {
            "error": f"Text extraction failed: {str(e)}"
        }
