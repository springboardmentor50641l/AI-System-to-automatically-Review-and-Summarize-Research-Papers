import json
from google import genai


# ---------------------------------------------------
# Core LLM Wrapper
# ---------------------------------------------------
def llm_generate(client, model_name: str, prompt: str) -> str:
    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )
    return response.text or ""


# ---------------------------------------------------
# Generic Critique Function
# ---------------------------------------------------
def critique_text(client, model_name: str, text: str, label: str) -> dict:
    prompt = f"""
You are a strict academic writing reviewer.

Task:
Critique the following generated section: {label}

Return output ONLY as valid JSON with this schema:
{{
  "score_0_to_10": number,
  "strengths": [string, ...],
  "issues": [string, ...],
  "missing_information": [string, ...],
  "revision_suggestions": [string, ...]
}}

Rules:
- Be realistic and strict
- Do not add external knowledge
- If the content is empty or weak, score low
- Focus on clarity, logical coherence, argument depth, academic tone, and faithfulness to provided material
- Penalize vague statements and repetition

Generated Text:
{text}
"""

    raw = llm_generate(client, model_name, prompt)

    try:
        return json.loads(raw)
    except Exception:
        return {
            "score_0_to_10": 0,
            "strengths": [],
            "issues": ["LLM returned invalid JSON critique output."],
            "missing_information": [],
            "revision_suggestions": [
                "Re-run critique.",
                "Ensure model strictly outputs valid JSON."
            ]
        }


# ---------------------------------------------------
# Generic Revision Function
# ---------------------------------------------------
def revise_text(client, model_name: str, text: str, critique_json: dict, label: str) -> str:
    prompt = f"""
You are an academic writing editor.

Task:
Revise the following section: {label}

Rules:
- Use ONLY the given text (do not add new facts)
- Apply the critique suggestions
- Improve clarity, structure, and academic rigor
- Strengthen analytical tone
- Remove redundancy
- Do NOT invent datasets, results, metrics, or citations
- If something is missing, explicitly state it is not specified in the analyzed literature

Original Text:
{text}

Critique JSON:
{json.dumps(critique_json, indent=2, ensure_ascii=False)}

Return ONLY the revised text.
"""

    return llm_generate(client, model_name, prompt).strip()


# ---------------------------------------------------
# Bundle Critique (Now Includes Discussion)
# ---------------------------------------------------
def critique_bundle(client, model_name: str, bundle: dict) -> dict:
    """
    bundle keys expected:
    abstract, methods, results, synthesis, discussion, references
    """

    report = {}

    sections = [
        ("abstract", "Abstract"),
        ("methods", "Methods Comparison"),
        ("results", "Results Analysis"),
        ("synthesis", "Literature Synthesis"),
        ("discussion", "Discussion / Critical Review"),
        ("references", "APA References")
    ]

    for key, label in sections:
        text = bundle.get(key, "") or ""
        report[key] = critique_text(client, model_name, text, label)

    return report


# ---------------------------------------------------
# Bundle Revision (Now Includes Discussion)
# ---------------------------------------------------
def revise_bundle(client, model_name: str, bundle: dict, critique_report: dict) -> dict:
    revised = {}

    sections = [
        ("abstract", "Abstract"),
        ("methods", "Methods Comparison"),
        ("results", "Results Analysis"),
        ("synthesis", "Literature Synthesis"),
        ("discussion", "Discussion / Critical Review"),
        ("references", "APA References")
    ]

    for key, label in sections:
        text = bundle.get(key, "") or ""
        critique_json = critique_report.get(key, {})
        revised[key] = revise_text(client, model_name, text, critique_json, label)

    return revised