"""
Workflow Controller
This file orchestrates the full AI research review pipeline.
"""

from modules.analyzer import analyze_papers
from modules.draft_generator import generate_draft
from modules.reviewer import review_paper


def run_workflow(texts, topic, mode):
    """
    Executes the research review workflow in sequence.

    Steps:
    1. Analyze papers
    2. Generate structured draft
    3. Review & refine output
    """

    if not texts or len(texts) < 2:
        return "At least two valid research papers are required for comparison."

    try:
        # ================= ANALYSIS =================
        analysis = analyze_papers(texts)

        # ================= DRAFT GENERATION =================
        draft = generate_draft(analysis, topic, mode)

        # ================= REVIEW =================
        final_output = review_paper(draft)

        if isinstance(final_output, list):
            final_output = "\n\n".join(str(x) for x in final_output)

        return final_output

    except Exception as e:
        return f"Workflow execution error: {str(e)}"
