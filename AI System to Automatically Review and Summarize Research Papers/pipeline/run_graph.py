from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
import json
import pandas as pd

from pipeline.graph import build_graph


# -------- CONFIG --------
METADATA_PATH = Path("data/metadata/selected_papers_metadata.csv")
OUTPUT_DIR = Path("data/sections")
OUTPUT_DIR.mkdir(exist_ok=True)


def normalize_topic(topic: str) -> str:
    return " ".join(topic.lower().split())



def get_pdfs_for_topic(topic: str):
    """
    Read metadata CSV and return PDF paths for the given topic.
    Topic matching is case-insensitive and whitespace-safe.
    """
    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            "Metadata file not found. Please run semantic search and download first."
        )

    df = pd.read_csv(METADATA_PATH)

    # Normalize stored topics
    df["topic_normalized"] = df["topic"].astype(str).apply(
    lambda x: " ".join(x.lower().split())
    )


    topic_norm = normalize_topic(topic)

    topic_df = df[
        (df["topic_normalized"] == topic_norm) &
        (df["has_pdf"] == True)
    ]

    if topic_df.empty:
        available_topics = df["topic"].dropna().unique().tolist()
        print("\nNo PDFs matched the given topic.")
        print("Available topics in metadata:")
        for t in available_topics:
            print(f" - {t}")
        return []

    return topic_df["pdf_path"].tolist()


def main():
    topic = input("Enter topic to process: ").strip()
    if not topic:
        print("Topic cannot be empty.")
        return

    pdf_paths = get_pdfs_for_topic(topic)

    if not pdf_paths:
        return

    print(f"\nFound {len(pdf_paths)} PDF(s) for topic '{topic}'")

    graph = build_graph()

    for pdf_path in pdf_paths:
        pdf = Path(pdf_path)

        if not pdf.exists():
            print(f"Skipping missing PDF: {pdf_path}")
            continue

        print(f"\nRunning LangGraph pipeline on: {pdf.name}")

        initial_state = {
            "pdf_path": str(pdf),
            "raw_text": None,
            "normalized_text": None,
            "sections": None
        }

        final_state = graph.invoke(initial_state)

        output_file = OUTPUT_DIR / f"{pdf.stem}_sections_langgraph.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                final_state["sections"],
                f,
                indent=2,
                ensure_ascii=False
            )

        print(f"Saved LangGraph output to {output_file}")

    print("\nTopic-level LangGraph processing completed.")


if __name__ == "__main__":
    main()
