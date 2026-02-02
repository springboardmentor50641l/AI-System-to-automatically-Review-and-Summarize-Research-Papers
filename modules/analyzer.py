# from google import genai
# from config import GEMINI_API_KEY, MODEL_NAME

# client = genai.Client(api_key=GEMINI_API_KEY)

# def analyze_papers(texts):
#     """
#     Analyzes and compares multiple research papers section-wise.
#     Works for 1 to 3 papers safely.
#     """

#     combined_text = ""

#     for idx, text in enumerate(texts, start=1):
#         combined_text += f"\n\n--- PAPER {idx} ---\n{text[:8000]}\n"

#     prompt = f"""
# You are an academic research analyst.

# Analyze and compare the following research papers section-wise.

# Tasks:
# 1. Identify key objectives of each paper
# 2. Compare methodologies used
# 3. Compare results and findings
# 4. Highlight similarities and differences
# 5. Extract major insights across papers

# Research Papers:
# {combined_text}

# Return a structured comparative analysis.
# """

#     response = client.models.generate_content(
#         model=MODEL_NAME,
#         contents=prompt
#     )

#     return response.text






#   --------------------------------------------------------------------------------------------- #

from llm import llm

def analyze_papers(texts):
    """
    Analyzes and compares up to 3 research papers section-wise.
    """

    combined_text = ""

    for idx, text in enumerate(texts, start=1):
        combined_text += f"\n\n--- PAPER {idx} ---\n{text[:8000]}\n"

    prompt = f"""
You are an academic research analyst.

Analyze and compare the following research papers section-wise.

Tasks:
1. Identify key objectives of each paper
2. Compare methodologies used
3. Compare results and findings
4. Highlight similarities and differences
5. Extract major insights across papers

Research Papers:
{combined_text}

Return a structured comparative analysis.
"""

    return llm.invoke(prompt).content
