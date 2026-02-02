import fitz  # PyMuPDF

def extract_text(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()
