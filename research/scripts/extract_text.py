import fitz  # PyMuPDF


def extract_raw_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    pages = []

    for page in doc:
        pages.append(page.get_text("text"))

    doc.close()
    return "\n".join(pages)


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("-\n", "")
    text = text.replace("\n\n", "\n")
    return text.strip()
