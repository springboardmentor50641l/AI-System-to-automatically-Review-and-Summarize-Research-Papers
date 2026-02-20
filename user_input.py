import os
import json
from pathlib import Path
from datetime import datetime

from pipelines.langgraph_text_extraction_graph import pipeline
from pipelines.draft_generation import generate_single_paper_draft, store_review_draft
from qaulity.review import run_review_evaluation
from comparision_id import generate_comparison_id
from pipelines.key_finding import run_key_findings 


def generate_review_from_pdf(pdf_path):

    comparison_id = generate_comparison_id()
    version = 1

    paper_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    print("🔍 Running extraction pipeline...")

    # STEP 1 — Extraction
    pipeline.invoke({
        "pdf_path": pdf_path,
        "paper_id": paper_id
    })

    # STEP 2 — Key Findings
    print("📌 Generating key findings...")

    run_key_findings(
        paper_id=paper_id,
        comparison_id=comparison_id
    )

    # STEP 3 — Load key findings
    print("📂 Loading key findings...")

    key_findings_path = (
        Path("text_extraction/output/key_findings")
        / comparison_id
        / f"key_findings_{paper_id}.json"
    )

    if not key_findings_path.exists():
        raise FileNotFoundError("Key findings file not found.")

    with open(key_findings_path, "r", encoding="utf-8") as f:
        key_findings_data = json.load(f)

    key_findings = key_findings_data.get("key_findings", [])

    # STEP 4 — Draft Generation
    print("📝 Generating draft review...")

    draft_text = generate_single_paper_draft(
        key_findings=key_findings,
        metadata={
            "title": "User Uploaded Paper",
            "authors": "Unknown",
            "year": "Unknown",
            "source": "User Upload"
        }
    )

    store_review_draft(
        draft_text=draft_text,
        comparison_id=comparison_id,
        version=version
    )

    # STEP 5 — Evaluation
    print("📊 Running evaluation...")

    run_review_evaluation(
        comparison_id=comparison_id,
        version=version
    )

    print("✅ Initial review generation complete.")

    return {
    "comparison_id": comparison_id,
    "version": version,
    "review_text": Path(
        f"text_extraction/output/review_comparison/final_review_{comparison_id}_v{version}.txt"
    ).read_text(encoding="utf-8")
    }
if __name__ == "__main__":

    pdf_path = r"papers\Quantum_Machine_Learning_260218_210359\Quantum_Machine_Learning_paper_3.pdf"

    result = generate_review_from_pdf(pdf_path)

    print("\n=== Review Generated ===\n")
    print(result["review_text"])    