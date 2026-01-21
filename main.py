import os
import time
from config import PAPER_DIR, MAX_PAPERS
from modules.planner import plan_research
from modules.paper_retrieval import search_papers
from modules.pdf_downloader import download_pdf
from modules.text_extractor import extract_text
from modules.analyzer import analyze_papers
from modules.draft_generator import generate_abstract, generate_methods, generate_results
from modules.reviewer import review_paper
from utils.apa_formatter import format_multiple_references

def run_pipeline(topic: str) -> str:
    os.makedirs(PAPER_DIR, exist_ok=True)

    # 1️ Planner
    plan = plan_research(topic)
    query = plan["search_query"]
    paper_count = plan["paper_count"]

    # 2️ Search papers
    papers = search_papers(query, limit=paper_count)
    if not papers:
        return "❌ No research papers found."

    texts = []
    valid_papers = []

    # 3️ Download + extract
    for i, paper in enumerate(papers):
        pdf = paper.get("openAccessPdf")
        if not pdf or not pdf.get("url"):
            continue

        filename = f"paper_{i}"
        path = f"{PAPER_DIR}/{filename}.pdf"

        try:
            download_pdf(pdf["url"], filename)
            time.sleep(2)
            text = extract_text(path)
            if text.strip():
                texts.append(text)
                valid_papers.append(paper)
        except:
            continue

    if not texts:
        return "❌ PDFs downloaded but text extraction failed."

    # 4️ Analysis
    analysis = analyze_papers(texts)

    # 5️ Writing
    abstract = generate_abstract(analysis)
    methods = generate_methods(analysis)
    results = generate_results(analysis)

    references = format_multiple_references(valid_papers)

    draft = f"""
ABSTRACT
{abstract}

METHODS
{methods}

RESULTS
{results}

REFERENCES
{references}
"""

    # 6️ Review
    return review_paper(draft)
