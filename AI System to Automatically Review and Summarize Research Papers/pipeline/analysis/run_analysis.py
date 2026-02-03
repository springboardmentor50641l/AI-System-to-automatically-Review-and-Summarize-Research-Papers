from pathlib import Path
import json
import pandas as pd
import os
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


def get_topic_from_metadata(topic: str):
    df = pd.read_csv(METADATA_PATH)
    df["topic_norm"] = df["topic"].apply(lambda x: " ".join(x.lower().split()))
    return topic, df[df["topic_norm"] == " ".join(topic.lower().split())]


def main():
    topic = input("Enter topic for analysis: ").strip()
    if not topic:
        print("Topic cannot be empty.")
        return

    topic, topic_df = get_topic_from_metadata(topic)

    if topic_df.empty:
        print("No metadata found for this topic.")
        return

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
        print("No section files found. Run run_graph.py first.")
        return

    print(f"\nFound {len(section_files)} paper(s) for analysis.")

    all_key_findings = []
    valid_papers = 0

    for section_file in section_files:
        with open(section_file, "r", encoding="utf-8") as f:
            sections = json.load(f)

        if not validate_sections(sections):
            print(f"Skipping invalid paper: {section_file.name}")
            continue

        print(f"Extracting key findings from {section_file.name}")
        findings = extract_key_findings(sections)
        all_key_findings.append(findings)
        valid_papers += 1

    if valid_papers == 0:
        print("No valid papers to analyze.")
        return

    # ---------- SINGLE PAPER CASE ----------
    if valid_papers == 1:
        print("\nOnly one valid paper found. Skipping cross-paper comparison.")
        final_draft = generate_analytical_draft(
            comparison_text=all_key_findings[0],
            topic=topic
        )

    # ---------- MULTI PAPER CASE ----------
    else:
        print("\nPerforming cross-paper comparison.")
        comparison = compare_key_findings(all_key_findings)
        final_draft = generate_analytical_draft(
            comparison_text=comparison,
            topic=topic
        )

    output_file = OUTPUT_DIR / f"{topic.replace(' ', '_')}_analytical_draft.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_draft)

    print(f"\nAnalytical draft saved to {output_file}")


if __name__ == "__main__":
    main()
