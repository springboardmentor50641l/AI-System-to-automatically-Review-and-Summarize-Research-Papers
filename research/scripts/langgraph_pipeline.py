from typing import TypedDict, Optional, Dict
from extract_text import extract_raw_text, normalize_text
from semantic_sectioning import section_paper_with_llm


class PaperState(TypedDict):
    pdf_path: str
    raw_text: Optional[str]
    clean_text: Optional[str]
    sections: Optional[Dict]


def load_paper_node(state: PaperState) -> PaperState:
    return state


def extract_text_node(state: PaperState) -> PaperState:
    raw_text = extract_raw_text(state["pdf_path"])
    state["raw_text"] = raw_text
    return state


def normalize_text_node(state: PaperState) -> PaperState:
    clean_text = normalize_text(state["raw_text"] or "")
    state["clean_text"] = clean_text
    return state


def semantic_sectioning_node(state: PaperState, client, model_name: str) -> PaperState:
    sections = section_paper_with_llm(state["clean_text"] or "", client, model_name)
    state["sections"] = sections
    return state


def validate_sections_node(state: PaperState) -> PaperState:
    if not isinstance(state.get("sections"), dict):
        raise ValueError("Invalid section output: sections must be a dict")
    return state


def store_sections_node(state: PaperState) -> PaperState:
    return state
