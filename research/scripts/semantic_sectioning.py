import json
from google import genai

SECTION_ONTOLOGY = [
    "abstract",
    "introduction",
    "background_work",
    "proposed_solution",
    "methodology",
    "results",
    "discussion",
    "conclusion",
    "references"
]


def build_prompt(text: str) -> str:
    return f"""
You are given the full text of a research paper.

Extract the paper into the following standard sections:
{SECTION_ONTOLOGY}

Rules:
- Do NOT summarize.
- Do NOT rewrite.
- Copy text exactly.
- If a section is missing, return empty string.
- Output MUST be valid JSON.
- JSON keys MUST exactly match the ontology.

Paper text:
{text}
"""


def section_paper_with_llm(clean_text: str, client: genai.Client, model_name: str) -> dict:
    response = client.models.generate_content(
        model=model_name,
        contents=build_prompt(clean_text),
    )

    output = response.text.strip()
    output = output.replace("```json", "").replace("```", "").strip()

    try:
        sections = json.loads(output)
    except Exception:
        raise ValueError("LLM output is not valid JSON:\n" + output)

    # Ontology enforcement
    final_sections = {}
    for sec in SECTION_ONTOLOGY:
        final_sections[sec] = str(sections.get(sec, "")).strip()

    return final_sections
