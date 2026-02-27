import pandas as pd
import os


def prepare_dataset(downloaded_papers, folder, expected_count=3):
    records = []

    for i in range(1, expected_count + 1):
        if i <= len(downloaded_papers):
            pdf_path = downloaded_papers[i - 1]

            records.append({
                "paper_id": i,
                "title": os.path.basename(pdf_path),
                "year": None,
                "url": None,
                "pdf_path": pdf_path,
                "availability_status": "AVAILABLE"
            })
        else:
            records.append({
                "paper_id": i,
                "title": None,
                "year": None,
                "url": None,
                "pdf_path": None,
                "availability_status": "NO_PDF"
            })

    return pd.DataFrame(records)
