import json
from typing import List, Dict
from google import genai


REQUIRED_SECTIONS = [
    "abstract",
    "introduction",
    "proposed_solution",
    "results",
    "conclusion"
]


def validate_sections(sections: dict) -> bool:
    for sec in REQUIRED_SECTIONS:
        if sec not in sections:
            return False
        if not str(sections[sec]).strip():
            return False
    return True


def extract_key_findings(sections: dict, client: genai.Client, model_name: str) -> str:
    prompt = f"""
You are an expert research analyst.

From the following research paper sections, extract the key findings
and main contributions made by the authors.

Rules:
- Use only the given content
- Do not add external knowledge
- Return findings as bullet points

Sections:
{json.dumps(sections, indent=2)}
"""
    response = client.models.generate_content(model=model_name, contents=prompt)
    return response.text.strip()


def compare_papers(papers: List[Dict], client: genai.Client, model_name: str) -> str:
    prompt = f"""
You are an expert conducting a comparative literature review.

Compare the following research papers based on:
1. Problem addressed
2. Methodology
3. Results
4. Strengths
5. Limitations

Papers:
{json.dumps(papers, indent=2)}

Produce a structured comparative analysis.
"""
    response = client.models.generate_content(model=model_name, contents=prompt)
    return response.text.strip()


def generate_draft(comparison_text: str, client: genai.Client, model_name: str) -> str:
    prompt = f"""
Using the following comparative analysis, generate a formal
academic literature review section.

Requirements:
- Formal academic tone
- Clear paragraph structure
- No hallucinated citations
- Do not add external references

Comparative Analysis:
{comparison_text}
"""
    response = client.models.generate_content(model=model_name, contents=prompt)
    return response.text.strip()
