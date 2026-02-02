# from google import genai
# from config import GEMINI_API_KEY, MODEL_NAME

# client = genai.Client(api_key=GEMINI_API_KEY)

# def review_paper(draft):
#     prompt = f"""
#     Review the following draft.
#     Suggest improvements and refine language.

#     Draft:
#     {draft}
#     """

#     return client.models.generate_content(
#         model=MODEL_NAME,
#         contents=prompt
#     ).text

# -    -------------------------------------------------------====================================----- #
# code with llm

from llm import llm

def review_paper(draft: str) -> str:
    """
    Reviews and refines the generated draft.
    Adds clarity, improves academic tone, and suggests refinements.
    """

    prompt = f"""
You are a peer reviewer for an academic journal.

Review the draft below and:
- Improve clarity and academic tone
- Remove redundancy
- Refine explanations if needed
- Keep the structure intact

Draft:
{draft}

Return the revised and polished version.
"""

    return llm.invoke(prompt).content
