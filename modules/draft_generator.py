
# code with llm
from llm import llm
from utils.llm_utils import normalize_llm_output
import datetime


def generate_draft(analysis, topic: str, mode: str) -> str:

    if isinstance(analysis, list):
        analysis = "\n\n".join(str(x) for x in analysis)

    if not analysis or not str(analysis).strip():
        return "Draft generation failed: Empty analysis."

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    prompt = f"""
You are an academic research writer.

Generate a structured research review with:

1. Abstract (max 100 words)
2. Methodology
3. Results
4. Key Insights
5. Limitations

Analysis:
{analysis}
"""

    try:
        response = llm.invoke(prompt)

        clean_text = normalize_llm_output(response.content)

        final_output = f"""
==================================================
AI Research Paper Review & Summarization System
==================================================

RESEARCH TOPIC : {topic}
INPUT MODE     : {mode.capitalize()}
GENERATED ON   : {timestamp}

--------------------------------------------------

{clean_text}

--------------------------------------------------
End of Report
--------------------------------------------------
"""

        return final_output.strip()

    except Exception as e:
        return f"Draft generation error: {str(e)}"


