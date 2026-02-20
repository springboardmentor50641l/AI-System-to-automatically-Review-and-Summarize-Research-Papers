from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from datetime import datetime
from pathlib import Path
from pipelines.references import format_apa_reference

import re
    
import json

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",timeout=120,temperature=0)


def load_comparison_result(comparison_id: str) -> dict:
    """
    Loads comparison JSON from text_extraction/output/review_comparison/
    """

    base_path = Path("text_extraction") / "output" / "review_comparison"

    file_name = f"review_comparison_{comparison_id}.json"
    comparison_path = base_path / file_name

    if not comparison_path.exists():
        raise FileNotFoundError(
            f"No comparison file found at {comparison_path}"
        )

    with open(comparison_path, "r", encoding="utf-8") as f:
        return json.load(f)

#final draft
def generate_full_draft(compare_result: dict, metadata_list: list):

    prompt = f"""
    You are an academic research writer generating a structured literature review draft.

    STRICT RULES:
    - Maintain formal academic tone.
    - Do NOT use conversational language.
    - Do NOT summarize papers individually.
    - Synthesize findings across studies.
    - Highlight methodological similarities and contrasts.
    - Avoid vague phrases such as "many studies suggest".
    - Do not fabricate citations.
    - No bullet points.
    - No commentary outside the required format.

    Length constraint:
    - 250–400 words total.

    FORMAT:

    ABSTRACT
    --------
    Provide a concise overview of the comparative theme and central contributions.

    METHODS
    -------
    Compare methodological approaches, datasets, architectures, and evaluation strategies.

    RESULTS
    -------
    Synthesize performance trends, strengths, limitations, and emerging patterns.

    Use the following structured comparison data:

    {json.dumps(compare_result)}
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    draft_text = response.content.strip()

    references = sorted(
        [format_apa_reference(meta) for meta in metadata_list]
    )

    full_text = draft_text + "\n\nREFERENCES\n----------\n" + "\n".join(references)

    return full_text


def build_final_literature_review(comparison_id, metadata_list, version=1):
    """
    Loads comparison JSON and generates full draft.
    Saves final_review_<comparison_id>.txt
    in text_extraction/output/review_comparison/
    """

    # 1️ Load structured comparison result
    compare_result = load_comparison_result(comparison_id)

    # 2️ Generate draft
    final_text = generate_full_draft(compare_result, metadata_list)

    # 3️ Save in same folder as comparison
    base_path = Path("text_extraction") / "output" / "review_comparison"
    output_file = base_path / f"final_review_{comparison_id}_v{version}.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"\nFinal review saved at: {output_file}")

    return final_text

def store_review_draft(draft_text: str, comparison_id: str, version: int) -> Path:

    output_dir = Path("text_extraction/output/review_comparison")
    output_dir.mkdir(parents=True, exist_ok=True)

    draft_path = output_dir / f"final_review_{comparison_id}_v{version}.txt"

    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(draft_text)

    print(f"[OK] Draft saved to {draft_path}")

    return draft_path
def generate_single_paper_draft(key_findings: list, metadata: dict):
    """
    Generates structured academic review for ONE paper.
    """

    prompt = f"""
    You are an academic reviewer writing a structured review of a single research paper.

    STRICT RULES:
    - Formal academic tone.
    - Do NOT fabricate content.
    - Base analysis strictly on provided sections.
    - No bullet points.
    - 250–400 words total.

    FORMAT:

    ABSTRACT
    --------
    Summarize the core research contribution and objective.

    METHODS
    -------
    Describe methodology, datasets, architecture, and experimental setup.

    RESULTS
    -------
    Analyze findings, strengths, and potential weaknesses.

    Provide critical but balanced academic insight.

    PAPER CONTENT:
    {json.dumps(key_findings)}
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    draft_text = response.content.strip()

    reference = format_apa_reference(metadata)

    full_text = draft_text + "\n\nREFERENCES\n----------\n" + reference
    
    return full_text

if __name__ == "__main__":

    # 🔹 Hardcoded comparison_id (from your sample file name)
    comparison_id = "comparison_20260216_204205_20260216_204627"

    # 🔹 Dummy metadata_list for testing
    metadata_list = [
        {
            "paper_id": "P1_nlp_260216_204210",
            "title": "SUPER-NATURALINSTRUCTIONS: Generalization via Instruction Tuning",
            "authors": "John Smith, Alice Lee",
            "year": 2022,
            "source": "Semantic Scholar"
        },
        {
            "paper_id": "P3_nlp_260216_204210",
            "title": "SVAMP: A Robust Challenge Dataset for Math Word Problems",
            "authors": "David Kumar, Sarah Chen",
            "year": 2021,
            "source": "Semantic Scholar"
        }
    ]

    try:
        print("\n Starting literature review generation...\n")

        final_text = build_final_literature_review(
            comparison_id=comparison_id,
            metadata_list=metadata_list
        )

        print("\n Literature review generated successfully!\n")
        print("----- Preview (first 500 chars) -----\n")
        print(final_text[:500])

    except Exception as e:
        print("\n Error occurred:")
        print(e)
