import json
from pathlib import Path
from text_extraction.text_extraction import (
    load_pdf,
    extract_text,
    clean_text,
    split_into_sections
)


def load_node(state):
    return state


def extract_node(state):
    pdf_path = Path(state["pdf_path"])  
    document = load_pdf(pdf_path)
    state["raw_text"] = extract_text(document)
    return state


def normalize_node(state):
    state["clean_text"] = clean_text(state["raw_text"])
    return state


def section_node(state):
    state["sections"] = split_into_sections(state["clean_text"])
    return state


def validate_node(state):
    required = [
        "abstract",
        "introduction",
        "methodology",
        "results",
        "discussion",
        "conclusion",
        "references"
    ]

    for key in required:
        if key not in state["sections"]:
            state["sections"][key] = ""

    return state


def store_node(state):
    output_path = state["pdf_path"].replace(".pdf", "_sections.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(state["sections"], f, indent=4)

    state["output_path"] = output_path
    return state
