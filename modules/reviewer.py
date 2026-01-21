from google import genai
from config import GEMINI_API_KEY, MODEL_NAME

client = genai.Client(api_key=GEMINI_API_KEY)

def review_paper(draft):
    return client.models.generate_content(
        model=MODEL_NAME,
        contents=f"Critically review and improve this paper:\n{draft}"
    ).text
