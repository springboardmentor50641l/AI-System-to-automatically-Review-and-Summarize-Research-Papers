from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
import json
import pandas as pd
from typing import Callable, Optional

from pipeline.graph import build_graph


# ------------CONFIG -------------
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

    df["topic_normalized"] = df["topic"].astype(str).apply(
        lambda x: " ".join(x.lower().split())
    )

    topic_norm = normalize_topic(topic)

    topic_df = df[
        (df["topic_normalized"] == topic_norm) &
        (df["has_pdf"] == True)
    ]

    if topic_df.empty:
        return []

    return topic_df["pdf_path"].tolist()



#----------MAIN GRAPH RUNNER----------

def run_graph_for_topic(
    topic: str,
    progress_callback: Optional[Callable[[str], None]] = None
):
    """
    Run LangGraph sectioning for all PDFs under a topic.

    progress_callback(message) can be passed by UI
    to stream execution updates.
    """

    pdf_paths = get_pdfs_for_topic(topic)

    if not pdf_paths:
        raise ValueError("No PDFs found for this topic.")

    if progress_callback:
        progress_callback(f"Found {len(pdf_paths)} PDF(s)")

    graph = build_graph()

    for pdf_path in pdf_paths:
        pdf = Path(pdf_path)

        if not pdf.exists():
            if progress_callback:
                progress_callback(f"Skipping missing PDF: {pdf_path}")
            continue

        if progress_callback:
            progress_callback(f"Processing: {pdf.name}")

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

        if progress_callback:
            progress_callback(f"Saved sections → {output_file.name}")

    if progress_callback:
        progress_callback("LangGraph processing completed.")



#------------ CLI MODE (optional)------------
def main():
    topic = input("Enter topic to process: ").strip()
    if not topic:
        print("Topic cannot be empty.")
        return

    run_graph_for_topic(topic, print)


if __name__ == "__main__":
    main()
