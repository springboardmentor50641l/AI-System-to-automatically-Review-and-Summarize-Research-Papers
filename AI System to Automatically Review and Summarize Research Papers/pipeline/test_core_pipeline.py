from pathlib import Path
import json
import os
from dotenv import load_dotenv
load_dotenv()

from pipeline.core.extract import extract_raw_text
from pipeline.core.normalize import normalize_text
from pipeline.core.section import semantic_sectioning


# -------- CONFIG --------
PDF_PATH = Path("data/raw_papers")  # folder containing PDFs
OUTPUT_DIR = Path("data/sections")
OUTPUT_DIR.mkdir(exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def main():
    pdf_files = list(PDF_PATH.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError("No PDF files found in data/raw_papers")

    for pdf in pdf_files[:1]:  # test with ONE paper first
        print(f"Processing: {pdf.name}")

        raw_text = extract_raw_text(pdf)
        clean_text = normalize_text(raw_text)

        sections = semantic_sectioning(clean_text, GEMINI_API_KEY)

        output_file = OUTPUT_DIR / f"{pdf.stem}_sections.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(sections, f, indent=2, ensure_ascii=False)

        print(f"Saved sections to {output_file}")


if __name__ == "__main__":
    main()
