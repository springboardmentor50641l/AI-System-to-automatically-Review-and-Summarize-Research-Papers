import pandas as pd

def prepare_dataset(downloaded_papers, folder, expected_count=3):
    records = []

    for i in range(1, expected_count + 1):
        if i <= len(downloaded_papers):
            paper = downloaded_papers[i - 1]
            records.append({
                "paper_id": i,
                "title": paper.get("title"),
                "year": paper.get("yearPublished"),
                "url": paper.get("downloadUrl"),
                "pdf_path": f"{folder}/paper_{i}.pdf",
                "availability_status": "AVAILABLE"
            })
        else:
            records.append({
                "paper_id": i,
                "title": None,
                "year": None,
                "url": None,
                "pdf_path": None,
                "availability_status": "NO_PDF_OR_URL"
            })
    return pd.DataFrame(records)
