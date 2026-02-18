from dataset.dataset_code import add_paper
import requests
import os
from datetime import datetime
from pathlib import Path
from pipelines.langgraph_text_extraction_graph import pipeline
from pipelines.key_finding import run_key_findings
from pipelines.compare_papers import run_review_builder
from comparision_id import generate_comparison_id
from pipelines.draft_generation import build_final_literature_review
from qaulity.review import run_review_evaluation, load_final_review
import json


APIKEY = "ZTfQ0m7guB358k9hi3j0T3wPVox2KsNB6IVTOhaq"


def generate_full_review(topic: str) -> dict:
    """
    Full research pipeline:
    Topic → Fetch PDFs → Extract → Compare → Draft → Evaluate

    Returns:
    {
        comparison_id,
        version,
        review_text,
        evaluation
    }
    """

    comparison_id = generate_comparison_id()

    index = 1
    pdf_paper = []

    safe_topic = topic.replace(" ", "_")
    time_stamp = datetime.now().strftime("%y%m%d_%H%M%S")
    folder = f"papers/{safe_topic}_{time_stamp}"
    os.makedirs(folder, exist_ok=True)

    # ----------------------------------
    # 1️⃣ FETCH PAPERS FROM SEMANTIC SCHOLAR
    # ----------------------------------

    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers = {"x-api-key": APIKEY}
    params = {
        "query": topic,
        "limit": 30,
        "fields": "title,year,authors,openAccessPdf"
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if "data" not in data:
        raise Exception(f"Semantic Scholar API error: {data}")

    for paper in data["data"]:
        if len(pdf_paper) == 6:
            break

        info = paper.get("openAccessPdf")
        if info and info.get("url"):
            pdf_paper.append(paper)

    # ----------------------------------
    # 2️⃣ DOWNLOAD PDFs
    # ----------------------------------

    downloaded_papers = []
    metadata_list = []

    for paper in pdf_paper:

        pdf_url = paper["openAccessPdf"]["url"]
        download = requests.get(pdf_url)

        if download.status_code == 200:

            filename = f"{folder}/{safe_topic}_paper_{index}.pdf"

            with open(filename, "wb") as f:
                f.write(download.content)

            title = paper["title"]
            paper_id = f"P{index}_{safe_topic}_{time_stamp}"
            authors = ", ".join([a["name"] for a in paper.get("authors", [])])
            year = paper.get("year", "Unknown")
            source = "Semantic Scholar"

            downloaded_papers.append((paper_id, filename))

            metadata = {
                "title": title,
                "authors": authors,
                "year": year,
                "source": source
            }

            metadata_list.append(metadata)

            add_paper(
                paper_id,
                title,
                authors,
                year,
                topic,
                source,
                filename,
                "yes",
                "Open-access PDF available"
            )

            index += 1

    # ----------------------------------
    # 3️⃣ TEXT EXTRACTION
    # ----------------------------------

    successful_papers = []

    for paper_id, filename in downloaded_papers:

        if len(successful_papers) == 2:
            break

        try:
            pipeline.invoke({
                "pdf_path": filename,
                "paper_id": paper_id
            })

            successful_papers.append(paper_id)

        except Exception:
            continue

    if len(successful_papers) < 2:
        raise Exception("Not enough successfully processed papers.")

    # ----------------------------------
    # 4️⃣ KEY FINDINGS + REVIEW BUILD
    # ----------------------------------

    for paper_id in successful_papers:
        run_key_findings(paper_id, comparison_id)

    run_review_builder(comparison_id)

    version = 1

    build_final_literature_review(
        comparison_id,
        metadata_list,
        version=version
    )

    run_review_evaluation(
        comparison_id,
        version=version
    )

    # ----------------------------------
    # 5️⃣ LOAD OUTPUTS
    # ----------------------------------

    review_text = load_final_review(comparison_id, version)

    evaluation_path = (
        f"text_extraction/output/review_comparison/"
        f"review_evaluation_{comparison_id}_v{version}.json"
    )

    with open(evaluation_path, "r", encoding="utf-8") as f:
        evaluation = json.load(f)

    return {
        "comparison_id": comparison_id,
        "version": version,
        "review_text": review_text,
        "evaluation": evaluation
    }
