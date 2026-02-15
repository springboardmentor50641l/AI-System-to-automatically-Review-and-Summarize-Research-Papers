import fitz  # PyMuPDF
import re
import json
from pathlib import Path
from datetime import datetime

# ----------- PATH CONFIG ----------- #

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

PDF_FILE = INPUT_DIR / "sample.pdf"

RAW_TEXT_OUTPUT = OUTPUT_DIR / "raw_text.txt"
CLEANED_TEXT_OUTPUT = OUTPUT_DIR / "cleaned_text.txt"
SECTIONS_OUTPUT = OUTPUT_DIR / "sections.json"

# ----------- SECTION PATTERNS ----------- #

SECTION_PATTERNS = {
    "abstract": r"^\s*abstract\s*$",
    "introduction": r"^\s*(\d+\.?|[ivxlcdm]+\.)?\s*introduction\s*$",
    "methodology": r"^\s*(\d+\.?|[ivxlcdm]+\.)?\s*(methodology|methods)\s*$",
    "results": r"^\s*(\d+\.?|[ivxlcdm]+\.)?\s*results\s*$",
    "discussion": r"^\s*(\d+\.?|[ivxlcdm]+\.)?\s*discussion\s*$",
    "conclusion": r"^\s*(\d+\.?|[ivxlcdm]+\.)?\s*conclusion\s*$",
    "references": r"^\s*references\s*$"
}

# --------------------------------------- #

def load_pdf(pdf_path: Path):
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    doc = fitz.open(pdf_path)
    print(f"PDF loaded | Pages: {len(doc)}")
    return doc


def extract_text(document):
    text_pages = []
    for page in document:
        page_text = page.get_text("text")
        if page_text:
            text_pages.append(page_text)
    return "\n".join(text_pages)


def clean_text(text: str):
    text = text.replace("-\n", "")            # fix hyphenated words
    text = re.sub(r"\r\n", "\n", text)        # normalize line endings
    text = re.sub(r"\n{2,}", "\n", text)      # collapse extra blank lines
    text = re.sub(r"[ \t]+", " ", text)       # normalize spaces
    return text.strip()


def split_into_sections(text: str):
    lines = text.split("\n")
    section_positions = []

    for i, line in enumerate(lines):
        stripped_line = line.strip()
        for section, pattern in SECTION_PATTERNS.items():
            if re.match(pattern, stripped_line, re.IGNORECASE):
                section_positions.append((section, i))
                break

    section_positions.sort(key=lambda x: x[1])

    sections = {}

    for idx, (section, start) in enumerate(section_positions):
        end = section_positions[idx + 1][1] if idx + 1 < len(section_positions) else len(lines)
        section_text = "\n".join(lines[start:end]).strip()
        sections[section] = section_text

    return sections


def save_outputs(raw_text, cleaned_text, sections):
    OUTPUT_DIR.mkdir(exist_ok=True)

    RAW_TEXT_OUTPUT.write_text(raw_text, encoding="utf-8")
    CLEANED_TEXT_OUTPUT.write_text(cleaned_text, encoding="utf-8")

    output_data = {
        "generated_on": datetime.utcnow().isoformat(),
        "total_sections": len(sections),
        "sections": sections
    }

    SECTIONS_OUTPUT.write_text(
        json.dumps(output_data, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print("raw_text.txt, cleaned_text.txt, sections.json saved")


def main():
    document = load_pdf(PDF_FILE)

    raw_text = extract_text(document)
    cleaned_text = clean_text(raw_text)
    sections = split_into_sections(cleaned_text)

    save_outputs(raw_text, cleaned_text, sections)



if __name__ == "__main__":
    main()
