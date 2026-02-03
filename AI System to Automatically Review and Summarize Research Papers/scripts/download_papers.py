import os
import time
import requests
import pandas as pd

PDF_DIR = "data/raw_papers"
os.makedirs(PDF_DIR, exist_ok=True)

#--------------DOWNLOAD FUNCTION--------------
def download_pdf(pdf_url, filename):
    response = requests.get(pdf_url)

    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        return True
    return False

#--------------PAPER DOWNLOAD----------------
def download_selected_papers(papers):
    for idx, paper in enumerate(papers, start=1):
        pdf_info = paper.get("openAccessPdf")

        if not pdf_info:
            print(f"Skipping paper {idx}: No open-access PDF")
            continue

        pdf_url = pdf_info.get("url")
        if not pdf_url:
            print(f"Skipping paper {idx}: PDF URL missing")
            continue

        paper_uid = paper.get("paperId", f"paper_{idx}")
        filename = os.path.join(PDF_DIR, f"{paper_uid}.pdf")

        print(f"Downloading paper {idx}...")
        success = download_pdf(pdf_url, filename)

        if success:
            print(f"Saved: {filename}")
        else:
            print(f"Failed to download paper {idx}")

        time.sleep(1)

#--------------METADATA--------------
METADATA_DIR = "data/metadata"
os.makedirs(METADATA_DIR, exist_ok=True)

def save_metadata(papers):
    records = []

    for idx, paper in enumerate(papers, start=1):
        paper_uid = paper.get("paperId", f"paper_{idx}")
        pdf_path = f"data/raw_papers/{paper_uid}.pdf"
        pdf_exists = os.path.exists(pdf_path)

        record = {
            "paper_id": idx,
            "title": paper.get("title"),
            "year": paper.get("year"),
            "url": paper.get("url"),
            "topic": paper.get("topic"),
            "has_pdf": pdf_exists,
            "pdf_path": pdf_path if pdf_exists else None,
            "selection_reason": "Top-ranked paper returned by Semantic Scholar relevance"
        }

        records.append(record)

    df = pd.DataFrame(records)

    output_path = os.path.join(METADATA_DIR, "selected_papers_metadata.csv")

    if os.path.exists(output_path):
        df.to_csv(output_path, mode="a", header=False, index=False)
    else:
        df.to_csv(output_path, header=True, index=False)

    print(f"\nMetadata saved to: {output_path}")
