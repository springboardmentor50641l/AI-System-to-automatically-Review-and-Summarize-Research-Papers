import datetime
from modules.analyzer import analyze_papers
from modules.draft_generator import generate_draft
from modules.reviewer import review_paper


def run_workflow(texts, topic, mode):
    """
    Executes complete AI review workflow.
    """

    try:
        # Step 1: Analyze
        analysis = analyze_papers(texts)

        # Step 2: Draft
        draft = generate_draft(analysis)

        # Step 3: Review
        reviewed = review_paper(draft)

        if isinstance(reviewed, list):
            reviewed = "\n\n".join(str(x) for x in reviewed)

        # Step 4: Add Header AFTER review
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        header = f"""
==================================================
AI Research Paper Review & Summarization System
==================================================

RESEARCH TOPIC : {topic}
INPUT MODE     : {mode.capitalize()}
GENERATED ON   : {timestamp}

--------------------------------------------------
"""

        final_output = header + "\n" + reviewed.strip() + "\n\n--------------------------------------------------\nEnd of Report\n--------------------------------------------------"

        return final_output

    except Exception as e:
        return f"Workflow execution error: {str(e)}"
