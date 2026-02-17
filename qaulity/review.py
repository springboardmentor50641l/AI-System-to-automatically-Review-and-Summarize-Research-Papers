from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from pathlib import Path
from datetime import datetime
import json
import re

# LLM CONFIG


model_name = "gemini-2.5-flash"

llm = ChatGoogleGenerativeAI(
    model=model_name,
    temperature=0,
    timeout=120
)

# JSON STRICT EXTRACTION


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



# AI EVALUATION


def evaluate_review(review_text: str) -> dict:
    """
    Uses Gemini to critique and score the review.
    Returns structured academic evaluation JSON.
    """

    prompt = f"""
    You are an expert academic peer reviewer.

    Evaluate the following literature review based on:

    1. Clarity & Coherence
    2. Depth of Analysis
    3. Methodological Comparison Quality
    4. Results Synthesis Strength
    5. Academic Writing Quality
    6. Reference Formatting

    Provide:
    - Strengths
    - Weaknesses
    - Missing Elements
    - Specific Revision Suggestions

    Also provide:
    - Sub-scores (0-10) for each criterion
    - Overall Quality Score (0-10)

    Return STRICT JSON only in this format:

    {{
    "strengths": "...",
    "weaknesses": "...",
    "missing_elements": "...",
    "revision_suggestions": "...",
    "sub_scores": {{
        "clarity_coherence": 0.0,
        "depth_of_analysis": 0.0,
        "methodology_comparison": 0.0,
        "results_synthesis": 0.0,
        "writing_quality": 0.0,
        "reference_formatting": 0.0
    }},
    "overall_quality_score": 0.0
    }}

    Literature Review:
    {review_text}
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    parsed = extract_json_strict(response.content)

    #  average
    sub_scores = parsed.get("sub_scores", {})
    if sub_scores:
        avg_score = sum(sub_scores.values()) / len(sub_scores)
        parsed["calculated_average_score"] = round(avg_score, 2)

    return parsed


# HEURISTIC SCORING


def heuristic_quality_score(review_text: str) -> float:
    score = 0

    word_count = len(review_text.split())

    if word_count > 800:
        score += 3
    elif word_count > 500:
        score += 2
    else:
        score += 1

    if "ABSTRACT" in review_text:
        score += 2
    if "METHODS" in review_text:
        score += 2
    if "RESULTS" in review_text:
        score += 2
    if "REFERENCES" in review_text:
        score += 1

    return min(score, 10)


# COMBINED SCORE (AI + HEURISTIC)

def compute_combined_score(ai_score: float, heuristic_score: float) -> float:
    """
    Weighted combination:
    70% AI + 30% heuristic
    """
    combined = (0.7 * ai_score) + (0.3 * heuristic_score)
    return round(combined, 2)


# D-SCORE (Deviation Score)


def compute_d_score(ai_score: float, heuristic_score: float) -> float:
    """
    Measures difference between AI and heuristic judgment.
    Useful diagnostic metric.
    """
    return round(abs(ai_score - heuristic_score), 2)


# LOAD FINAL REVIEW TEXT


def load_final_review(comparison_id: str, version: int = 1) -> str:
    base_path = Path("text_extraction/output/review_comparison")

    file_name = f"final_review_{comparison_id}_v{version}.txt"


    review_path = base_path / file_name

    if not review_path.exists():
        raise FileNotFoundError(f"No review file found at {review_path}")

    with open(review_path, "r", encoding="utf-8") as f:
        return f.read()


# STORE EVALUATION REPORT

def store_evaluation_report(result: dict, comparison_id: str, version: int) -> Path:
    output_dir = Path("text_extraction/output/review_comparison")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"review_evaluation_{comparison_id}_v{version}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"[OK] Evaluation report saved to {output_path}")
    return output_path



# MAIN RUN FUNCTION 


def run_review_evaluation(comparison_id: str, version: int = 1) -> Path:
    """
    Loads review text → evaluates → computes scores → stores versioned JSON.
    """

    print(f"[INFO] Running evaluation v{version}...")

    review_text = load_final_review(comparison_id, version=version)

    ai_evaluation = evaluate_review(review_text)
    ai_score = ai_evaluation.get("overall_quality_score", 0.0)

    heuristic_score = heuristic_quality_score(review_text)
    combined_score = compute_combined_score(ai_score, heuristic_score)
    d_score = compute_d_score(ai_score, heuristic_score)

    final_report = {
        "comparison_id": comparison_id,
        "version": version,
        "timestamp": datetime.now().isoformat(),
        "ai_evaluation": ai_evaluation,
        "heuristic_score": heuristic_score,
        "combined_score": combined_score,
        "d_score": d_score
    }

    return store_evaluation_report(final_report, comparison_id, version)




if __name__ == "__main__":

    #  actual comparison_id
    comparison_id = "comparison_20260217_223809"

    #  This is original draft → version 1
    version = 1

    try:
        print("\n[TEST] Running Review Evaluation Module...\n")

        output_path = run_review_evaluation(
            comparison_id=comparison_id,
            version=version
        )

        print("\n[TEST SUCCESS] Evaluation completed.")
        print(f"Saved at: {output_path}")

    except Exception as e:
        print("\n[TEST ERROR]")
        print(e)
