import os
import re
import json
import sys
import argparse
import subprocess
from dotenv import load_dotenv
from google import genai
from draft_structurer import structure_and_export
from langgraph.graph import StateGraph, END

from langgraph_pipeline import (
    PaperState,
    load_paper_node,
    extract_text_node,
    normalize_text_node,
    semantic_sectioning_node,
    validate_sections_node,
    store_sections_node
)

from analysis_llm import (
    validate_sections,
    extract_key_findings,
    compare_papers,
    generate_draft
)

load_dotenv()


# -----------------------------
# Helpers
# -----------------------------
def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def run_cmd(cmd: list[str]):
    print("\n" + "=" * 70)
    print("RUN:", " ".join(cmd))
    print("=" * 70 + "\n")

    result = subprocess.run(cmd, shell=False)
    if result.returncode != 0:
        print("\n❌ Command failed:", " ".join(cmd))
        sys.exit(result.returncode)


# -----------------------------
# Load Gemini Config
# -----------------------------
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL")

if not API_KEY:
    raise ValueError("Missing GEMINI_API_KEY or GOOGLE_API_KEY in .env")

if not MODEL_NAME:
    raise ValueError("Missing GEMINI_MODEL in .env")

client = genai.Client(api_key=API_KEY)


# -----------------------------
# Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECTIONS_DIR = os.path.join(BASE_DIR, "data", "semantic_sections")
ANALYSIS_DIR = os.path.join(BASE_DIR, "data", "analysis_llm")

os.makedirs(SECTIONS_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)


# -----------------------------
# LangGraph Pipeline Builder
# -----------------------------
def build_pipeline():
    graph = StateGraph(PaperState)

    graph.add_node("load", load_paper_node)
    graph.add_node("extract", extract_text_node)
    graph.add_node("normalize", normalize_text_node)

    graph.add_node(
        "section",
        lambda state: semantic_sectioning_node(state, client, MODEL_NAME)
    )

    graph.add_node("validate", validate_sections_node)
    graph.add_node("store", store_sections_node)

    graph.set_entry_point("load")

    graph.add_edge("load", "extract")
    graph.add_edge("extract", "normalize")
    graph.add_edge("normalize", "section")
    graph.add_edge("section", "validate")
    graph.add_edge("validate", "store")
    graph.add_edge("store", END)

    return graph.compile()


# -----------------------------
# Sectioning Runner
# -----------------------------
def run_langgraph_sectioning(pipeline, pdf_dir):
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("❌ No PDFs found in:", pdf_dir)
        return []

    sectioned_papers = []

    for file in pdf_files:
        pdf_path = os.path.join(pdf_dir, file)
        print("\n📄 Processing:", file)

        initial_state: PaperState = {
            "pdf_path": pdf_path,
            "raw_text": None,
            "clean_text": None,
            "sections": None
        }

        final_state = pipeline.invoke(initial_state)
        sections = final_state["sections"]

        # Save sections JSON
        out_name = file.replace(".pdf", ".json")
        out_path = os.path.join(SECTIONS_DIR, out_name)

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(sections, f, indent=2, ensure_ascii=False)

        print("✅ Saved sections:", out_path)

        sectioned_papers.append({
            "paper_file": file,
            "sections": sections
        })

    return sectioned_papers


# -----------------------------
# Analysis Runner
# -----------------------------
def run_analysis(sectioned_papers, topic_slug):
    topic_analysis_dir = os.path.join(ANALYSIS_DIR, topic_slug)
    os.makedirs(topic_analysis_dir, exist_ok=True)

    processed = []
    key_findings_map = {}

    for item in sectioned_papers:
        file = item["paper_file"]
        sections = item["sections"]

        if not validate_sections(sections):
            print("⚠️ Skipping analysis:", file)
            continue

        print("🔍 Extracting key findings:", file)
        findings = extract_key_findings(sections, client, MODEL_NAME)

        key_findings_map[file] = findings

        processed.append({
            "paper_file": file,
            "sections": sections,
            "key_findings": findings
        })

    # Save key findings
    with open(os.path.join(topic_analysis_dir, "key_findings.json"), "w", encoding="utf-8") as f:
        json.dump(key_findings_map, f, indent=2, ensure_ascii=False)

    if len(processed) < 2:
        print("⚠️ Need at least 2 valid papers for comparison.")
        return

    print("\n📌 Cross-paper comparison running...")
    comparison = compare_papers(processed, client, MODEL_NAME)

    with open(os.path.join(topic_analysis_dir, "comparison.txt"), "w", encoding="utf-8") as f:
        f.write(comparison)

    print("📝 Draft generation running...")
    draft = generate_draft(comparison, client, MODEL_NAME)

    draft_path = os.path.join(topic_analysis_dir, "literature_review_draft.txt")

    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(draft)

    print("✅ Draft saved:", draft_path)

    # 🔥 AUTO STRUCTURE STEP
    print("\n📚 Structuring final draft...")
    structure_and_export(topic_slug)

    print("\n✅ Analysis + Structuring complete for topic:", topic_slug)


# -----------------------------
# MAIN
# -----------------------------
def main():
    parser = argparse.ArgumentParser(description="Run full pipeline: download -> section -> analyze")
    parser.add_argument("topic", type=str, help="Research topic")
    parser.add_argument("--limit", type=int, default=10, help="Number of PDFs to download")
    args = parser.parse_args()

    topic = args.topic.strip()
    limit = args.limit

    topic_slug = slugify(topic)

    # Step 1: Download PDFs
    run_cmd([
        sys.executable,
        os.path.join(BASE_DIR, "scripts", "search_and_download.py"),
        topic,
        "--limit",
        str(limit)
    ])

    # Step 2: Build pipeline + sectioning
    pdf_dir = os.path.join(BASE_DIR, "papers", topic_slug)

    pipeline = build_pipeline()
    sectioned_papers = run_langgraph_sectioning(pipeline, pdf_dir)

    # Step 3: Analysis
    # note: run_analysis requires the slug so it can create the analysis directory
    run_analysis(sectioned_papers, topic_slug)


if __name__ == "__main__":
    main()
