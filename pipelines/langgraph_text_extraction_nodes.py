from text_extraction.text_extraction_utils import (load_pdf,extract_raw_text,clean_text,split_into_sections)
from typing import TypedDict, Optional, Dict
from pathlib import Path
from langgraph.graph import StateGraph, END
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


SECTION_ONTOLOGY = ["abstract","introduction","background","related work","methodology","proposed solution","results","discussion","conclusion"]
PROMPT = """
You are given the raw text of a research paper.

Task:
Extract verbatim text that explicitly belongs to each of the following sections:
{sections}

Rules:
- Only classify text if the section is clearly marked by headings or titles.
- Do NOT infer or guess.
- If a section is not explicitly present, return an empty string.
- Copy text exactly as it appears.
- Do NOT rewrite, summarize, or reorder.
- Output MUST be valid JSON.
- Keys MUST exactly match the section names.
- Return ONE JSON object, nothing else.

Paper text:
{text}
"""
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",timeout=120,temperature=0)
    
    


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
   
def empty_sections():
    return {section: "" for section in SECTION_ONTOLOGY}

def semantic_sectioning_node(state: PaperState) -> PaperState:
    MAX_CHARS = 12000  # safe for Gemini Flash

    if "clean_text" not in state or not state["clean_text"]:
        raise ValueError("No clean_text available for sectioning")

    text = state["clean_text"]

    # HARD TRIM to avoid Gemini timeout
    if len(text) > 12000:
        print(f"Trimming text from {len(text)} to 12000 characters")
        text = text[:12000]

    try:
        response = llm.invoke([
            HumanMessage(
                content=PROMPT.format(
                    sections=SECTION_ONTOLOGY,
                    text=text
                )
            )
        ])

        raw = response.content if hasattr(response, "content") else response
        sections = json.loads(raw)

        final = {section: sections.get(section, "") for section in SECTION_ONTOLOGY}
        state["sections"] = final

        print("Semantic sectioning completed")

    except Exception as e:
        raise RuntimeError(f"Semantic sectioning failed: {e}")

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
 def extract_key_findings(sections: dict, llm) -> str:
    prompt = f"""
    You are an expert research analyst.

    From the following extracted research paper sections,
    identify the key findings and main contributions.

    Rules:
    - Use only the given content
    - Do not introduce external knowledge
    - Do not speculate
    - Return 3–5 bullet points

    Sections:
    {sections}
    """

    response = llm.invoke([HumanMessage(content=prompt)])

    return response.content
def compare_papers(processed_papers: list[dict], llm) -> str:
    prompt = f"""
    You are conducting a comparative literature review.

    Compare the following research papers based on:
    1. Problem addressed
    2. Methodology
    3. Results
    4. Strengths
    5. Limitations

    Papers:
    {processed_papers}

    Produce a concise, structured comparison.
    """

    response = llm.invoke([HumanMessage(content=prompt)])

    return response.content

def generate_draft(comparison_text: str, llm) -> str:
    prompt = f"""
    Using the following comparative analysis, generate
    a formal academic literature review section.

    Requirements:
    - Formal academic tone
    - Clear paragraph structure
    - No hallucinated citations
    - No new claims beyond the analysis

    Comparative Analysis:
    {comparison_text}
    """

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    return response.content
   
     
if __name__ == "__main__":
    result = pipeline.invoke({"pdf_path": r""})
    print(result["sections"])


