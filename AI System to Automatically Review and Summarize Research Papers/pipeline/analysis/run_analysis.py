from pathlib import Path
import json
import pandas as pd
import os
from typing import Callable, Optional

os.environ["LANGCHAIN_TRACING_V2"] = "0"
os.environ["LANGCHAIN_TRACING"] = "false"

from pipeline.analysis.paper_analysis import (
    validate_sections,
    extract_key_findings,
    compare_key_findings,
    generate_analytical_draft
)

# -------- CONFIG --------
SECTIONS_DIR = Path("data/sections")
METADATA_PATH = Path("data/metadata/selected_papers_metadata.csv")
OUTPUT_DIR = Path("data/analysis_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def normalize_topic(topic: str) -> str:
    return " ".join(topic.lower().split())


def get_topic_dataframe(topic: str):
    if not METADATA_PATH.exists():
        raise FileNotFoundError("Metadata file not found.")

    df = pd.read_csv(METADATA_PATH)
    df["topic_norm"] = df["topic"].astype(str).apply(normalize_topic)

    topic_norm = normalize_topic(topic)
    return df[df["topic_norm"] == topic_norm]


# -------- MAIN ANALYSIS FUNCTION --------
def run_analysis_for_topic(
    topic: str,
    progress_callback: Optional[Callable[[str], None]] = None
):
    topic_df = get_topic_dataframe(topic)

    if topic_df.empty:
        raise ValueError("No metadata found for this topic.")

    section_files = []

    for pdf_path in topic_df["pdf_path"]:
        if not isinstance(pdf_path, str):
            continue

        pdf = Path(pdf_path)
        if not pdf.exists():
            continue

        stem = pdf.stem
        section_file = SECTIONS_DIR / f"{stem}_sections_langgraph.json"

        if section_file.exists():
            section_files.append(section_file)

    if not section_files:
        raise ValueError("No section files found. Run graph stage first.")

    if progress_callback:
        progress_callback(f"Found {len(section_files)} paper(s) for analysis.")

    all_key_findings = []
    valid_papers = 0

    for section_file in section_files:
        with open(section_file, "r", encoding="utf-8") as f:
            sections = json.load(f)

        if not validate_sections(sections):
            if progress_callback:
                progress_callback(f"Skipping invalid paper: {section_file.name}")
            continue

        if progress_callback:
            progress_callback(f"Extracting key findings: {section_file.name}")

        findings = extract_key_findings(sections)
        all_key_findings.append(findings)
        valid_papers += 1

    if valid_papers == 0:
        raise ValueError("No valid papers to analyze.")

    # -------- SINGLE PAPER --------
    if valid_papers == 1:
        if progress_callback:
            progress_callback("Single paper detected. Skipping comparison.")

        final_draft = generate_analytical_draft(
            comparison_text=all_key_findings[0],
            topic=topic
        )

    # -------- MULTIPLE PAPERS --------
    else:
        if progress_callback:
            progress_callback("Performing cross-paper comparison.")

        comparison = compare_key_findings(all_key_findings)

        final_draft = generate_analytical_draft(
            comparison_text=comparison,
            topic=topic
        )

    output_file = OUTPUT_DIR / f"{topic.replace(' ', '_')}_analytical_draft.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_draft)

    if progress_callback:
        progress_callback(f"Analytical draft saved to {output_file.name}")

    return final_draft


# -------- CLI MODE --------
def main():
    topic = input("Enter topic for analysis: ").strip()
    if not topic:
        print("Topic cannot be empty.")
        return

    run_analysis_for_topic(topic, print)


if __name__ == "__main__":
    main()
