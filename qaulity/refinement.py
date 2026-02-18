from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from datetime import datetime
from pathlib import Path
import re
import json

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    timeout=120,
    temperature=0
)



# Strict JSON extraction helper

def extract_json_strict(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("Empty LLM output")

    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found")

    return json.loads(match.group(0))


# Load original draft

def load_review_draft(comparison_id: str, version: int) -> str:
    review_path = Path(
        f"text_extraction/output/review_comparison/"
        f"final_review_{comparison_id}_v{version}.txt"
    )

    if not review_path.exists():
        raise FileNotFoundError(f"Draft not found: {review_path}")

    return review_path.read_text(encoding="utf-8")

# Load evaluation JSON
def load_evaluation(comparison_id: str, version: int) -> dict:
    evaluation_path = Path(
        f"text_extraction/output/review_comparison/"
        f"review_evaluation_{comparison_id}_v{version}.json"
    )

    if not evaluation_path.exists():
        raise FileNotFoundError(f"Evaluation not found: {evaluation_path}")

    with open(evaluation_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Refinement Logic

def refine_review_with_feedback(original_review: str, critique: dict) -> str:
    """
    Uses structured critique feedback to produce a refined review.
    """

    ai_eval = critique.get("ai_evaluation", {})

    missing_elements = "\n".join(ai_eval.get("missing_elements", []))
    revision_suggestions = "\n".join(ai_eval.get("revision_suggestions", []))

    prompt = f"""
    You are an academic editor improving a literature review.

    Use ONLY the provided critique feedback to revise the review.

    CRITICAL INSTRUCTIONS:
    - Preserve the exact section structure and headings.
    - Do NOT modify, rewrite, reformat, add, remove, or correct anything inside the REFERENCES section.
    - The REFERENCES section must remain EXACTLY as provided.
    - If critique comments relate to references, ignore them.
    - Do NOT fabricate or infer missing citation details.
    - Do NOT add new references.
    - Revise ONLY the main body of the review (from ABSTRACT through CONCLUSION).
    - Keep all existing in-text citations unchanged.
    - Do NOT introduce new citations.
    - Improve clarity, analytical depth, coherence, and transitions only where critique explicitly requires it.

    Additional Rules:
    - Do NOT remove valid content.
    - Address all weaknesses mentioned in the critique.
    - Integrate missing conceptual elements into existing sections (do not create new sections).
    - Deepen comparative analysis where needed.
    - Maintain formal academic tone.

    -------------------
    ORIGINAL REVIEW:
    -------------------
    {original_review}

    -------------------
    CRITIQUE:
    -------------------
    Strengths:
    {ai_eval.get("strengths", "")}

    Weaknesses:
    {ai_eval.get("weaknesses", "")}

    Missing Elements:
    {missing_elements}

    Revision Suggestions:
    {revision_suggestions}

    Return ONLY the fully revised literature review.
    Do NOT output commentary or explanations.

    """

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()


# Store refined draft

def store_refined_review(refined_text: str, comparison_id: str, new_version: int) -> Path:

    output_dir = Path("text_extraction/output/review_comparison")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"final_review_{comparison_id}_v{new_version}.txt"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(refined_text)

    print(f"[OK] Refined review saved to {output_path}")
    return output_path


# Run refinement pipeline

def run_review_refinement(comparison_id: str, version: int):

    print("[INFO] Loading original draft...")
    original_review = load_review_draft(comparison_id, version)

    print("[INFO] Loading evaluation feedback...")
    evaluation = load_evaluation(comparison_id, version)

    print("[INFO] Refining review...")
    refined_review = refine_review_with_feedback(original_review, evaluation)

    new_version = version + 1

    output_path = store_refined_review(
        refined_review,
        comparison_id,
        new_version
    )

    print("[OK] Refinement complete.")
    return output_path


def refine_once(comparison_id: str, current_version: int):
    """
    Refines one version and returns updated info for UI.
    """

    # Step 1: refine current version
    run_review_refinement(comparison_id, version=current_version)

    new_version = current_version + 1

    # Step 2: evaluate the new version
    run_review_evaluation(comparison_id, version=new_version)

    return f"Refinement complete.\nNew Version: v{new_version}"

from qaulity.review import load_final_review

def refine_once(comparison_id: str, current_version: int):

    run_review_refinement(comparison_id, version=current_version)

    new_version = current_version + 1

    run_review_evaluation(comparison_id, version=new_version)

    refined_text = load_final_review(comparison_id, version=new_version)

    return refined_text, new_version


# Standalone test execution

if __name__ == "__main__":

    comparison_id = "comparison_20260217_223809"

    # We are refining Version 1 → producing Version 2
    version = 1  

    print("[INFO] Running Review Refinement Module...")

    run_review_refinement(
        comparison_id=comparison_id,
        version=version
    )

    print("[SUCCESS] Version 2 draft generated.")

