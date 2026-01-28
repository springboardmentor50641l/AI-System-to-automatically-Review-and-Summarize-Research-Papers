from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
import json

from pipeline.graph import build_graph


# -------- CONFIG --------
PDF_DIR = Path("data/raw_papers")
OUTPUT_DIR = Path("data/sections")
OUTPUT_DIR.mkdir(exist_ok=True)


def main():
    graph = build_graph()

    pdf_files = list(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError("No PDFs found in data/raw_papers")

    # Run on ONE paper only (intentional)
    pdf = pdf_files[0]
    print(f"Running LangGraph pipeline on: {pdf.name}")

    initial_state = {
        "pdf_path": str(pdf),
        "raw_text": None,
        "normalized_text": None,
        "sections": None
    }

    final_state = graph.invoke(initial_state)

    output_file = OUTPUT_DIR / f"{pdf.stem}_sections_langgraph.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_state["sections"], f, indent=2, ensure_ascii=False)

    print(f"Saved LangGraph output to {output_file}")


if __name__ == "__main__":
    main()
