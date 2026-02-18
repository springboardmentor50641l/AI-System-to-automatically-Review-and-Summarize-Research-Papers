from llm import llm
from utils.llm_utils import normalize_llm_output


def generate_draft(analysis: str) -> str:

    if isinstance(analysis, list):
        analysis = "\n\n".join(str(x) for x in analysis)

    if not analysis or not str(analysis).strip():
        return ""

    prompt = f"""
You are an academic research writer.

Generate a structured research review with:

1. Abstract (max 100 words)
2. Methodology
3. Results
4. Key Insights
5. Limitations

Return ONLY the structured report.
Do NOT add any extra commentary.
Do not use markdown symbols (*, #).


Analysis:
{analysis}
"""

    try:
        response = llm.invoke(prompt)
        return normalize_llm_output(response.content)

    except Exception:
        return ""
