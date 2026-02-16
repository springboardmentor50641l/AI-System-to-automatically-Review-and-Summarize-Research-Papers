
from llm import llm
from utils.llm_utils import normalize_llm_output


def review_paper(draft: str) -> str:
    """
    Reviews and refines the generated draft.
    Returns ONLY the polished report.
    """

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
Return ONLY the final revised report.
Do NOT add any explanation.
Do NOT add commentary.
Do NOT say what you changed.
Do NOT add introductory sentences.

Draft:
{draft}
"""

    try:
        response = llm.invoke(prompt)
        return normalize_llm_output(response.content)

    except Exception as e:
        print(f"[Reviewer Error] {e}")
        return draft
