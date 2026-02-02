import requests
from config import SEMANTIC_SCHOLAR_API_KEY

BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

def search_papers(topic, limit=3):
    headers = {"x-api-key": SEMANTIC_SCHOLAR_API_KEY}
    params = {
        "query": topic,
        "limit": limit * 2,
        "fields": "title,authors,year,openAccessPdf"
    }

    res = requests.get(BASE_URL, headers=headers, params=params)
    res.raise_for_status()

    papers = []
    for p in res.json().get("data", []):
        if p.get("openAccessPdf") and p["openAccessPdf"].get("url"):
            papers.append(p)
        if len(papers) == limit:
            break

    return papers
