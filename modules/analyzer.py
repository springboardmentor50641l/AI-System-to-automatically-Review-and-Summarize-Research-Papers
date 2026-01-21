from google import genai
from config import GEMINI_API_KEY, MODEL_NAME

client = genai.Client(api_key=GEMINI_API_KEY)

def analyze_papers(texts):
    prompt = f"""
    Analyze and compare the following research papers.
    Identify key themes, similarities, and differences.

    Papers:
    {texts}
    """
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text
