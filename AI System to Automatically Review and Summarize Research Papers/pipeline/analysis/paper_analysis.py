import os
import json
from typing import Dict, List
from dotenv import load_dotenv
import os

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


# ---------------- LLM CONFIG ----------------
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0
    )


# ---------------- VALIDATION ----------------
def validate_sections(sections: Dict[str, str]) -> bool:
    """
    Validate that the paper has enough meaningful content
    to proceed with analysis.
    """
    if not sections or not isinstance(sections, dict):
        return False

    non_empty_sections = [
        content for content in sections.values()
        if isinstance(content, str) and content.strip()
    ]

    # Require at least 3 meaningful sections
    return len(non_empty_sections) >= 3



# ---------------- KEY FINDINGS ----------------
def extract_key_findings(sections: Dict[str, str]) -> str:
    """
    Extract key findings and contributions from a paper.
    """
    llm = get_llm()

    prompt = f"""
You are an expert research analyst.

From the following research paper sections, extract:
- Key findings
- Main contributions
- Important results

Rules:
- Use ONLY the given content
- Do NOT add external knowledge
- Do NOT summarize sections
- Return bullet points only

Sections:
{json.dumps(sections, indent=2)}
"""

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    return response.content.strip()


# ---------------- CROSS-PAPER COMPARISON ----------------
def compare_key_findings(findings: List[str]) -> str:
    """
    Compare key findings across multiple papers.
    """
    llm = get_llm()

    prompt = f"""
You are a research analyst.

Compare the following key findings from multiple research papers.

Your task:
- Identify common themes
- Highlight similarities and differences
- Note conflicting or unique insights

Rules:
- Do NOT add new knowledge
- Base analysis strictly on the given findings
- Write in clear analytical language

Key Findings:
{json.dumps(findings, indent=2)}
"""

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    return response.content.strip()


# ---------------- DRAFT GENERATION ----------------
def generate_analytical_draft(comparison_text: str, topic: str) -> str:
    """
    Generate a structured analytical draft based on comparison.
    """
    llm = get_llm()

    prompt = f"""
You are an academic writing assistant.

Based on the following comparative analysis, generate
a structured analytical draft on the topic:

Topic:
{topic}

Guidelines:
- Academic tone
- Logical flow
- No external information
- No citations required
- Do NOT mention paper names explicitly

Comparative Analysis:
{comparison_text}
"""

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    return response.content.strip()
