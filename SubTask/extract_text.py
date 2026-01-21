import fitz  # PyMuPDF
from pathlib import Path
import json

#-------------PATH CONFIGURATION-------------
PDF_PATH = Path("input/research_paper.pdf")
OUTPUT_DIR = Path("output")

RAW_TEXT_PATH = OUTPUT_DIR / "raw_text.txt"
SECTIONS_PATH = OUTPUT_DIR / "sections.json"

OUTPUT_DIR.mkdir(exist_ok=True)

#-------------SECTION HEADERS---------------
SECTION_HEADERS = [
    "Abstract",
    "Keywords",
    "Introduction",
    "Related Work",
    "Methodology",
    "Methods",
    "Results",
    "Discussion",
    "Conclusion",
    "References"
]

#----------TEXT EXTRACTION FUNCTION----------
def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract full text from a PDF file using PyMuPDF."""
    text_content = []

    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            page_text = page.get_text()
            if page_text:
                text_content.append(page_text)

    return "\n".join(text_content)

#----------SECTION SPLITTING FUNCTION-------
def split_into_sections(text: str, headers: list) -> dict:
    sections = {}
    current_section = "Preamble"
    sections[current_section] = []

    lines = text.split("\n")

    for line in lines:
        line_clean = line.strip()

        for header in headers:
            if line_clean.lower() == header.lower():
                current_section = header
                sections[current_section] = []
                break
        else:
            sections[current_section].append(line)

    # Join lines into text blocks
    for key in sections:
        sections[key] = "\n".join(sections[key]).strip()

    return sections

#-------------SAVE FUNCTIONS---------------
def save_text_to_file(text: str, output_path: Path):
    output_path.write_text(text, encoding="utf-8")

def save_sections_to_json(sections: dict, output_path: Path):
    output_path.write_text(
        json.dumps(sections, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

#-------------------MAIN--------------------
if __name__ == "__main__":
    raw_text = extract_text_from_pdf(PDF_PATH)
    save_text_to_file(raw_text, RAW_TEXT_PATH)

    sections = split_into_sections(raw_text, SECTION_HEADERS)
    save_sections_to_json(sections, SECTIONS_PATH)

    print("Text extraction and section splitting completed.")
