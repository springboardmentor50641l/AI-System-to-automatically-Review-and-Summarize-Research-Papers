import fitz  # PyMuPDF
from pathlib import Path

#-------------PATH CONFIGURATION-------------
PDF_PATH = Path("input/research_paper.pdf")
OUTPUT_DIR = Path("output")
OUTPUT_TXT = OUTPUT_DIR / "raw_text.txt"

OUTPUT_DIR.mkdir(exist_ok=True)

#----------TEXT EXTRACTION FUNCTION----------
def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract full text from a PDF file using PyMuPDF."""
    text_content = []

    with fitz.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            page_text = page.get_text()
            if page_text:
                text_content.append(page_text)

    return "\n".join(text_content)

#-------------SAVE TEXT FUNCTION-------------
def save_text_to_file(text: str, output_path: Path):
    """Save extracted text to a .txt file."""
    output_path.write_text(text, encoding="utf-8")

#-------------------MAIN--------------------
if __name__ == "__main__":
    extracted_text = extract_text_from_pdf(PDF_PATH)
    save_text_to_file(extracted_text, OUTPUT_TXT)
    print(f"Text extraction completed. Output saved at: {OUTPUT_TXT}")
