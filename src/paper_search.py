import os
import requests
from dataset import Paper, ResearchDataset

SEMANTIC_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "").strip()
if not API_KEY:
    raise RuntimeError("SEMANTIC_SCHOLAR_API_KEY not set")

HEADERS = {
    "x-api-key": API_KEY,
    "User-Agent": "Infosys-Research-Project/1.0",
    "Accept": "application/json"
}

BASE_PDF_DIR = "../data/pdfs"
os.makedirs(BASE_PDF_DIR, exist_ok=True)

def automated_paper_search(topic: str, max_papers: int = 3) -> ResearchDataset:
    # ---- create topic-wise folder ----
    safe_topic = topic.lower().replace(" ", "_")
    topic_dir = os.path.join(BASE_PDF_DIR, safe_topic)
    os.makedirs(topic_dir, exist_ok=True)

    # ---- Semantic Scholar search ----
    params = {
        "query": topic,
        "limit": 3,
        "fields": "title,abstract,year,openAccessPdf"
    }

    r = requests.get(
        SEMANTIC_SEARCH_URL,
        headers=HEADERS,
        params=params,
        timeout=30
    )

    if r.status_code != 200:
        raise RuntimeError(
            f"Semantic Scholar API error {r.status_code}: {r.text}"
        )

    results = r.json()["data"]

    papers = []
    count = 0

    # ---- paper selection + PDF download ----
    for p in results:
        if p.get("abstract") and p.get("openAccessPdf"):
            pdf_url = p["openAccessPdf"]["url"]
            pdf_path = os.path.join(topic_dir, f"paper_{count}.pdf")

            pdf_response = requests.get(pdf_url, timeout=30)
            with open(pdf_path, "wb") as f:
                f.write(pdf_response.content)

            paper = Paper(
                title=p["title"],
                year=p.get("year"),
                pdf_path=pdf_path,
                reason="Relevant topic and open-access PDF available"
            )

            papers.append(paper)
            count += 1

        if count == max_papers:
            break

    dataset = ResearchDataset(papers=papers)
    return dataset
