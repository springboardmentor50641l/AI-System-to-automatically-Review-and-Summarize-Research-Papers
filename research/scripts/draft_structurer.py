import os
import json
import argparse
from dotenv import load_dotenv
from google import genai

load_dotenv()


# -----------------------------
# Helpers
# -----------------------------
def llm_generate(client, model_name: str, prompt: str) -> str:
    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )
    return response.text or ""


def slugify(text: str) -> str:
    import re
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


# -----------------------------
# Main Structuring Function
# -----------------------------
def structure_and_export(topic_slug: str):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Input path (analysis_llm)
    input_path = os.path.join(
        BASE_DIR,
        "data",
        "analysis_llm",
        topic_slug,
        "literature_review_draft.txt"
    )

    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"literature_review_draft.txt not found for topic: {topic_slug}"
        )

    # Output path (drafts folder)
    drafts_topic_dir = os.path.join(
        BASE_DIR,
        "data",
        "drafts",
        topic_slug
    )

    os.makedirs(drafts_topic_dir, exist_ok=True)

    json_output_path = os.path.join(
        drafts_topic_dir,
        "literature_review_structured.json"
    )

    txt_output_path = os.path.join(
        drafts_topic_dir,
        "literature_review_structured.txt"
    )

    # Load Gemini
    API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    MODEL_NAME = os.getenv("GEMINI_MODEL")

    if not API_KEY:
        raise ValueError("Missing GEMINI_API_KEY or GOOGLE_API_KEY")

    if not MODEL_NAME:
        raise ValueError("Missing GEMINI_MODEL")

    client = genai.Client(api_key=API_KEY)

    # Read draft
    with open(input_path, "r", encoding="utf-8") as f:
        draft_text = f.read()

    # Structuring prompt
    prompt = f"""
You are an academic writing assistant.

Task:
Convert the following literature review draft into structured JSON.

Return ONLY valid JSON in this format:

{{
  "abstract": "",
  "methods_comparison": "",
  "results_synthesis": "",
  "discussion": "",
  "conclusion": "",
  "references": ""
}}

Rules:
- Do NOT add new information.
- Only reorganize and clean.
- Preserve all original meaning.
- Remove generic placeholder labels or enumerations such as "Paper 1", "Paper 2", etc.
- Omit any extraneous numbering or bullet lists that were not part of the original text.
- If section missing, leave empty.
- Output ONLY JSON.

Draft:
{draft_text}
"""

    response = llm_generate(client, MODEL_NAME, prompt)

    try:
        structured = json.loads(response)
    except Exception:
        raise ValueError("Model did not return valid JSON.")

    # Save JSON
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2, ensure_ascii=False)

    # Convert to formatted text
    formatted_text = f"""
ABSTRACT
{structured.get("abstract", "")}

METHODS COMPARISON
{structured.get("methods_comparison", "")}

RESULTS SYNTHESIS
{structured.get("results_synthesis", "")}

DISCUSSION
{structured.get("discussion", "")}

CONCLUSION
{structured.get("conclusion", "")}

REFERENCES
{structured.get("references", "")}
"""

    with open(txt_output_path, "w", encoding="utf-8") as f:
        f.write(formatted_text.strip())

    print("\n✅ Structured draft saved to:")
    print("   ", json_output_path)
    print("   ", txt_output_path)

    return structured


# -----------------------------
# CLI Entry
# -----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("topic", type=str, help="Topic slug (e.g., ai_ethics)")
    args = parser.parse_args()

    topic_slug = slugify(args.topic)
    structure_and_export(topic_slug)import os
import json
import argparse
from dotenv import load_dotenv
from google import genai

load_dotenv()


# -----------------------------
# Helpers
# -----------------------------
def llm_generate(client, model_name: str, prompt: str) -> str:
    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )
    return response.text or ""


def slugify(text: str) -> str:
    import re
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


# -----------------------------
# Main Structuring Function
# -----------------------------
def structure_and_export(topic_slug: str):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Input path (analysis_llm)
    input_path = os.path.join(
        BASE_DIR,
        "data",
        "analysis_llm",
        topic_slug,
        "literature_review_draft.txt"
    )

    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"literature_review_draft.txt not found for topic: {topic_slug}"
        )

    # Output path (drafts folder)
    drafts_topic_dir = os.path.join(
        BASE_DIR,
        "data",
        "drafts",
        topic_slug
    )

    os.makedirs(drafts_topic_dir, exist_ok=True)

    json_output_path = os.path.join(
        drafts_topic_dir,
        "literature_review_structured.json"
    )

    txt_output_path = os.path.join(
        drafts_topic_dir,
        "literature_review_structured.txt"
    )

    # Load Gemini
    API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    MODEL_NAME = os.getenv("GEMINI_MODEL")

    if not API_KEY:
        raise ValueError("Missing GEMINI_API_KEY or GOOGLE_API_KEY")

    if not MODEL_NAME:
        raise ValueError("Missing GEMINI_MODEL")

    client = genai.Client(api_key=API_KEY)

    # Read draft
    with open(input_path, "r", encoding="utf-8") as f:
        draft_text = f.read()

    # Structuring prompt
    prompt = f"""
You are an academic writing assistant.

Task:
Convert the following literature review draft into structured JSON.

Return ONLY valid JSON in this format:

{{
  "abstract": "",
  "methods_comparison": "",
  "results_synthesis": "",
  "discussion": "",
  "conclusion": "",
  "references": ""
}}

Rules:
- Do NOT add new information.
- Only reorganize and clean.
- Preserve all original meaning.
- Remove generic placeholder labels or enumerations such as "Paper 1", "Paper 2", etc.
- Omit any extraneous numbering or bullet lists that were not part of the original text.
- If section missing, leave empty.
- Output ONLY JSON.

Draft:
{draft_text}
"""

    response = llm_generate(client, MODEL_NAME, prompt)

    try:
        structured = json.loads(response)
    except Exception:
        raise ValueError("Model did not return valid JSON.")

    # Save JSON
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2, ensure_ascii=False)

    # Convert to formatted text
    formatted_text = f"""
ABSTRACT
{structured.get("abstract", "")}

METHODS COMPARISON
{structured.get("methods_comparison", "")}

RESULTS SYNTHESIS
{structured.get("results_synthesis", "")}

DISCUSSION
{structured.get("discussion", "")}

CONCLUSION
{structured.get("conclusion", "")}

REFERENCES
{structured.get("references", "")}
"""

    with open(txt_output_path, "w", encoding="utf-8") as f:
        f.write(formatted_text.strip())

    print("\n✅ Structured draft saved to:")
    print("   ", json_output_path)
    print("   ", txt_output_path)

    return structured


# -----------------------------
# CLI Entry
# -----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("topic", type=str, help="Topic slug (e.g., ai_ethics)")
    args = parser.parse_args()

    topic_slug = slugify(args.topic)
    structure_and_export(topic_slug)
