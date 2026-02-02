from google import genai
from config import GEMINI_API_KEY, MODEL_NAME
def plan_research(topic: str) -> str:
    return f"""
    Research Topic: {topic}
    Scope: Identify 3 relevant peer-reviewed papers.
    Focus: Abstract, Methods, Results comparison.
    """

client = genai.Client(api_key=GEMINI_API_KEY)

def plan_research(topic: str) -> dict:
    prompt = f"""
Refine the academic search query for topic: "{topic}"
Decide paper count (max 3)

Return JSON:
{{"search_query": "...", "paper_count": 3}}
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    import json
    try:
        return json.loads(response.text)
    except:
        return {"search_query": topic, "paper_count": 3}
