from text_extraction.text_extraction_utils import (load_pdf,extract_raw_text,clean_text,split_into_sections)
from typing import TypedDict, Optional, Dict
from pathlib import Path
from langgraph.graph import StateGraph, END
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


SECTION_ONTOLOGY = ["abstract","introduction","background","related work","methodology","proposed solution","results","discussion","conclusion"]
PROMPT = """
You are given the full text of a research paper.

Your task is to divide the paper into the following logical sections:
{sections}

Rules:
- Do NOT summarize or rewrite the text.
- Do NOT add new content.
- Extract the original text verbatim.
- If a section is missing, return an empty string for it.
- Return the output strictly as valid JSON.
- Use section names exactly as provided.

Paper text:
{text}
"""
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview", timeout=30, # prevents infinite hanging 
    temperature=0)
    
    


class PaperState(TypedDict):
    pdf_path: str
    raw_text: Optional[str]
    clean_text: Optional[str]
    sections: Optional[Dict]


def load_paper_node(state: PaperState) -> PaperState:
    # Basic validation
    if not Path(state["pdf_path"]).exists():
        raise FileNotFoundError(f"PDF not found: {state['pdf_path']}")
    return state

def extract_text_node(state: PaperState) -> PaperState:
    pdf_path = Path(state["pdf_path"])
    
    pdf_doc = load_pdf(pdf_path)
    raw_text = extract_raw_text(pdf_doc)
    
    state["raw_text"] = raw_text
    return state

def normalize_text_node(state: PaperState) -> PaperState:
    cleaned = clean_text(state["raw_text"])
    state["clean_text"] = cleaned
    return state

def semantic_sectioning_node(state: PaperState) -> PaperState:
    text = state["clean_text"]
    response = llm.invoke([HumanMessage(content=PROMPT.format(sections=SECTION_ONTOLOGY, text=text))])
    state["sections"] = json.loads(response.content)
    return state

section_headers = ["abstract","introduction","related work","method","methodology","results","discussion","conclusion","references"]
def section_split_node(state: PaperState) -> PaperState:
    sections = split_into_sections(state["clean_text"],section_headers)
    state["sections"] = sections
    return state
def validate_sections_node(state: PaperState) -> PaperState:
    sections = state["sections"]
    if not isinstance(sections, dict):
        raise ValueError("Sections must be a dictionary")
    if not sections:
        raise ValueError("Sections dictionary is empty")
    return state


def store_sections_node(state: PaperState) -> PaperState:
    output_path = Path("text_extraction/output/semantic_sections.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(state["sections"], f, indent=2, ensure_ascii=False)
    print(f"Semantic sections saved to {output_path}")
    return state
     
if __name__ == "__main__":
    result = pipeline.invoke({"pdf_path": r"text_extraction\sample_paper\test_paper.pdf"})
    print(result["sections"])


