from llm import llm
from utils.llm_utils import normalize_llm_output


def review_paper(draft: str) -> str:

    if not draft or not str(draft).strip():
        return ""

    prompt = f"""
You are an academic journal peer reviewer.

Revise the draft below to:
- Improve academic tone
- Improve clarity
- Remove redundancy
- Strengthen logical flow

IMPORTANT:
Do NOT remove or modify the header section if present.
Return ONLY the final revised report.

Draft:
{draft}
"""

    try:
        response = llm.invoke(prompt)
        return normalize_llm_output(response.content)

    except Exception:
        return draft
