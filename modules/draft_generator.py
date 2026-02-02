# from google import genai
# from config import GEMINI_API_KEY, MODEL_NAME

# client = genai.Client(api_key=GEMINI_API_KEY)

# def generate_draft(analysis):
#     prompt = f"""
#     From the analysis below, generate:
#     1. Abstract (max 100 words)
#     2. Methods comparison
#     3. Results synthesis
#     4. Key insights

#     Analysis:
#     {analysis}
#     """

#     return client.models.generate_content(
#         model=MODEL_NAME,
#         contents=prompt
#     ).text

#  -------------------------------------------------------====================================----- #
# code with llm
from llm import llm

def generate_draft(analysis: str) -> str:
    """
    Generates a structured research review draft from analysis.
    Sections:
    - Abstract (max 100 words)
    - Methods comparison
    - Results synthesis
    - Key insights
    """

    prompt = f"""
You are an academic research writer.

Using the analysis below, generate a structured research review with:

1. Abstract (maximum 100 words)
2. Methods comparison
3. Results synthesis
4. Key insights

Analysis:
{analysis}

Write in formal academic style.
"""

    return llm.invoke(prompt).content

