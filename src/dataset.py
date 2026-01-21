import pandas as pd

def prepare_dataset(papers, folder, topic):
    records = []

    for i, paper in enumerate(papers):
        records.append({
            "topic": topic,
            "title": paper.get("title"),
            "authors": ", ".join(
                author.get("name", "")
                for author in paper.get("authors", [])
            ),
            "year": paper.get("yearPublished"),
            "citations": paper.get("citationCount"),
            "pdf_path": f"{folder}/paper_{i+1}.pdf"
        })

    return pd.DataFrame(records)
