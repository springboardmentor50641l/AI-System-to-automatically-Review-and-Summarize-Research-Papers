from text_extraction.text_extraction_utils import (save_clean_text,load_pdf,extract_raw_text,clean_text,split_into_sections)
from typing import TypedDict, Optional, Dict
from pathlib import Path
from datetime import datetime
from langgraph.graph import StateGraph, END
import json
import re

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


SECTION_ONTOLOGY = ["abstract","introduction","background","related work","methodology","proposed solution","results","discussion","conclusion"]
PROMPT = """
You are given raw text of a research paper.

Extract ONLY the following sections:
{sections}

Rules:

1. Identify sections using explicit headings or common academic synonyms.
2. Map similar headings to the closest section in the list.
3. If a section does not exist, return an empty string.
4. Ignore references, bibliography, appendix, page numbers, and website navigation text.
5. If a section is extremely long, return only the first 2000 words of that section.
6. Do NOT summarize. Copy the detected section text as-is.
7. Output MUST be valid JSON.
8. Keys MUST exactly match the provided section names.
9. Return ONLY one JSON object and nothing else.

Paper text:
{text}
"""
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",timeout=120,temperature=0)
    
    

class PaperState(TypedDict, total=False):
    pdf_path: str
    raw_text: str
    clean_text: str
    sections: Dict[str, str]
    paper_id: str
    clean_text_file: str
    sections_file: str



def load_paper_node(state: PaperState) -> PaperState:
    # Basic validation
    if not Path(state["pdf_path"]).exists():
        raise FileNotFoundError(f"PDF not found: {state['pdf_path']}")
    if "paper_id" not in state:
        raise ValueError("paper_id must be provided from metadata stage")
    return {**state}

def extract_text_node(state: PaperState) -> PaperState:
    pdf_path = Path(state["pdf_path"])
    
    pdf_doc = load_pdf(pdf_path)
    raw_text = extract_raw_text(pdf_doc)
    
    return {
        **state,
        "raw_text": raw_text}

def normalize_text_node(state: PaperState) -> PaperState:
    raw = state["raw_text"]

    print("RAW_TEXT TYPE:", type(raw))
    print("RAW_TEXT LENGTH:", len(raw) if raw else "EMPTY")

    cleaned = clean_text(raw)

    print("CLEAN_TEXT TYPE:", type(cleaned))
    print("CLEAN_TEXT LENGTH:", len(cleaned) if cleaned else "EMPTY")

    return {**state, "clean_text": cleaned}

def store_clean_text_node(state: PaperState) -> PaperState:

    clean_text = state.get("clean_text")
    paper_id = state.get("paper_id")

    if not clean_text:
        raise ValueError("No clean_text found")

    if not paper_id:
        raise ValueError("paper_id missing in state")

    output_dir = Path("text_extraction/output/clean_text")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"clean_text_{paper_id}.txt"

    save_clean_text(clean_text, output_path)

    return {
        **state,
        "clean_text_file": str(output_path)
    }
  
def empty_sections():
    return {section: "" for section in SECTION_ONTOLOGY}

def extract_json(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text)
    text = re.sub(r"```$", "", text)
    return text.strip()

    
def semantic_sectioning_node(state: PaperState) -> PaperState:
    print("ENTER semantic_sectioning_node")
    print("STATE KEYS:", state.keys())

    #clean text must exist
    if "clean_text" not in state or not state["clean_text"].strip():
        raise ValueError("No clean_text available for semantic sectioning")

    text = state["clean_text"]

    #LLM INVOCATION
    response = llm.invoke([
        HumanMessage(
            content=PROMPT.format(
                sections=SECTION_ONTOLOGY,
                text=text
            )
        )
    ])

    raw = response.content if hasattr(response, "content") else response
    print("RAW LLM OUTPUT (repr):", repr(raw))

    #  LLM output 
    if not raw or not raw.strip():
        raise ValueError("LLM returned EMPTY response — aborting sectioning")

    # Clean + parse JSON 
    cleaned_raw = extract_json(raw)

    try:
        parsed = json.loads(cleaned_raw)
    except json.JSONDecodeError as e:
        print("INVALID JSON FROM LLM:")
        print(cleaned_raw)
        raise ValueError("LLM returned invalid JSON") from e

    #  Normalize sections
    sections = {
        section: parsed.get(section, "").strip()
        for section in SECTION_ONTOLOGY
    }

    # ---- Content validation ----
    if all(not v for v in sections.values()):
        raise ValueError("All extracted sections are empty — rejecting output")

    print("SECTIONING SUCCESSFUL")
    return {
        **state,
        "sections": sections
    }
def validate_sections_node(state: PaperState) -> PaperState:
    sections = state["sections"]
    if not isinstance(sections, dict):
        raise ValueError("Sections must be a dictionary")
    if not sections:
        raise ValueError("Sections dictionary is empty")
    
    return {**state}
def store_sections_node(state: PaperState) -> PaperState:
    print("ENTER store_sections_node")

    sections = state.get("sections")
    paper_id = state.get("paper_id")

    if not sections:
        raise ValueError("No sections found to store")

    if not paper_id:
        raise ValueError("paper_id missing in state")

    output_dir = Path("text_extraction/output/sectioned_data")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"sectioned_data_{paper_id}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sections, f, indent=2, ensure_ascii=False)

    print(f"Sections saved to: {output_path}")

    return {
        **state,
        "sections_file": str(output_path)
    }



if __name__ == "__main__":
    result = pipeline.invoke({"pdf_path": r""})
    print(result["sections"])


