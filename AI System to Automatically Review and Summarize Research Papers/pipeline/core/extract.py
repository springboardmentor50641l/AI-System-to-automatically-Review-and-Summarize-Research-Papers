import fitz  # PyMuPDF
from pathlib import Path

def extract_raw_text(pdf_path: Path) -> str:
    """
    Extract the full raw text from a research paper PDF.
    The output preserves reading order as much as possible
    and is suitable for downstream semantic processing.
    """
    document = fitz.open(pdf_path)
    extracted_pages = []

    for page in document:
        page_text = page.get_text("text")
        if page_text:
            extracted_pages.append(page_text)

    return "\n".join(extracted_pages)
