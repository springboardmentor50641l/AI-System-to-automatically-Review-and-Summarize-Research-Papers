from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from datetime import datetime
from pathlib import Path
from pipelines.method import generate_methods
from pipelines.references import format_apa_reference
from pipelines.result import generate_results
from pipelines.abstract import generate_abstract
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
    abstract = generate_abstract(compare_result)
    methods = generate_methods(compare_result)
    results = generate_results(compare_result)

    references = sorted(
        [format_apa_reference(meta) for meta in metadata_list]
    )

    full_text = f"""
ABSTRACT
--------
{abstract}

METHODS
-------
{methods}

RESULTS
-------
{results}

REFERENCES
----------
""" + "\n".join(references)

    return full_text

def build_final_literature_review(comparison_id: str, metadata_list: list):

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
    output_file = base_path / f"final_review_{comparison_id}_v1.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"\n  Final review saved at: {output_file}")

    return final_text
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
