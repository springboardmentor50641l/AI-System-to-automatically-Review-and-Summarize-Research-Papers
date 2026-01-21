from google import genai
from config import GEMINI_API_KEY, MODEL_NAME

client = genai.Client(api_key=GEMINI_API_KEY)

def generate_abstract(analysis):
    return client.models.generate_content(
        model=MODEL_NAME,
        contents=f"Write a 100-word abstract:\n{analysis}"
    ).text

def generate_methods(analysis):
    return client.models.generate_content(
        model=MODEL_NAME,
        contents=f"Summarize methodologies:\n{analysis}"
    ).text

def generate_results(analysis):
    return client.models.generate_content(
        model=MODEL_NAME,
        contents=f"Synthesize results:\n{analysis}"
    ).text
