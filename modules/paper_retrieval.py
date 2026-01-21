import requests
from config import SEMANTIC_SCHOLAR_API_KEY

BASE_URL = "https://api.semanticscholar.org/graph/v1"

def search_papers(topic, limit=5):
    headers = {}
    if SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY

    r = requests.get(
        f"{BASE_URL}/paper/search",
        params={
            "query": topic,
            "limit": limit,
            "fields": "title,abstract,year,authors,url,openAccessPdf"
        },
        headers=headers,
        timeout=20
    )

    if r.status_code != 200:
        return []

    return r.json().get("data", [])
