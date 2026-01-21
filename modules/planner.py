from google import genai
from config import GEMINI_API_KEY, MODEL_NAME

client = genai.Client(api_key=GEMINI_API_KEY)

def plan_research(topic: str) -> dict:
    prompt = f"""
    Create a research plan for the topic: {topic}

    Respond strictly in JSON:
    {{
      "search_query": "...",
      "paper_count": 5
    }}
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        import json
        data = json.loads(response.text)
        return {
            "search_query": data.get("search_query", topic),
            "paper_count": int(data.get("paper_count", 5))
        }
    except:
        return {"search_query": topic, "paper_count": 5}
