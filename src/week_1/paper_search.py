import os
import requests
from dotenv import load_dotenv
from dataset import Paper, ResearchDataset
import time

load_dotenv()

SEMANTIC_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

HEADERS = {
    "x-api-key": API_KEY,
    "User-Agent": "Infosys-Research-Project/1.0",
    "Accept": "application/json"
}

BASE_PDF_DIR = "pdfs"
os.makedirs(BASE_PDF_DIR, exist_ok=True)


def automated_paper_search(topic: str, max_papers: int = 3) -> ResearchDataset:
    if not API_KEY:
        raise RuntimeError("SEMANTIC_SCHOLAR_API_KEY not found in .env file")

    safe_topic = topic.lower().replace(" ", "_")
    topic_dir = os.path.join(BASE_PDF_DIR, safe_topic)
    os.makedirs(topic_dir, exist_ok=True)

    params = {
        "query": topic,
        "limit": max_papers * 5,  # get more results to filter valid PDFs
        "fields": "title,year,openAccessPdf"
    }

    
    for _ in range(3):
        r = requests.get(SEMANTIC_SEARCH_URL, headers=HEADERS, params=params, timeout=30)
        if r.status_code == 200:
            break
        time.sleep(2)
    else:
        raise RuntimeError(f"Semantic Scholar API error {r.status_code}: {r.text}")

    results = r.json().get("data", [])

    papers = []
    count = 0

    for p in results:
        if count == max_papers:
            break

        if not p.get("openAccessPdf"):
            continue

        pdf_url = p["openAccessPdf"].get("url")
        if not pdf_url:
            continue

        try:
            pdf_response = requests.get(pdf_url, stream=True, timeout=30)

            content_type = pdf_response.headers.get("Content-Type", "").lower()

            # only allow real PDFs
            if "application/pdf" not in content_type:
                continue

            pdf_path = os.path.join(topic_dir, f"paper_{count+1}.pdf")

            with open(pdf_path, "wb") as f:
                for chunk in pdf_response.iter_content(1024):
                    f.write(chunk)

            paper = Paper(
                title=p.get("title", "Unknown Title"),
                year=p.get("year"),
                pdf_path=pdf_path,
                reason="Verified open-access PDF"
            )

            papers.append(paper)
            count += 1

        except:
            continue

    if len(papers) < max_papers:
        raise RuntimeError("Could not find 3 valid PDF papers (only real PDFs are accepted).")

    return ResearchDataset(papers=papers)
