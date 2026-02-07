import fitz  
from pathlib import Path
import re 
import json

fitz.TOOLS.mupdf_display_errors(False)
#Load file and print total number of pages
def load_pdf(pdf_path):
    #file not found error
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found at: {pdf_path}")

    try:
        document = fitz.open(pdf_path)
        print(f"PDF loaded successfully")
        print(f"Total pages: {len(document)}")
        return document
    #runtime error
    except Exception as e:
        raise RuntimeError(f"Failed to open PDF: {e}")
def extract_raw_text(pdf_document):
    all_pages_text = []

    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]

        blocks = page.get_text("blocks")
        page_text = " ".join(
            block[4] for block in blocks if block[4].strip()
        )

        if page_text.strip():
            all_pages_text.append(page_text)

        print(
            f"Page {page_number + 1} extracted chars:",
            len(page_text)
        )

    full_text = "\n".join(all_pages_text)
    if not full_text.strip():
        raise ValueError(
            "PDF text extraction failed. "
            "Likely scanned or unsupported layout.")

    return full_text

# Save raw text to file
def save_raw_text_to_file(text, output_path):
    #save raw data ina a file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(text)

    print(f"Raw text saved to: {output_path}")
#clean text
def clean_text(text: str) -> str:
    # Remove common academic noise
    text = re.sub(r"(?i)preprint.*?\n", "", text)
    text = re.sub(r"(?i)under review.*?\n", "", text)
    # Fix excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()  
#clean text saved      
def save_clean_text(text: str, output_path: Path) -> None:
    # Create folder if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Write text to file
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(text)
    print(f"Cleaned text saved to: {output_path}")    
#section headers
section_headers = ["abstract","introduction","related work","method","methodology","results","discussion","conclusion","references"]
#split text into sections
def split_into_sections(text: str, headers: list) -> dict:
    sections = {}
    current_section = "preamble"
    sections[current_section] = []
    lines = text.split("\n")
    for line in lines:
        line_clean = line.strip()
        line_lower = line_clean.lower()
        if line_lower in headers:
            current_section = line_lower
            sections[current_section] = []
        else:
            sections[current_section].append(line)
    # Join lines back
    for key in sections:
        sections[key] = "\n".join(sections[key]).strip()
    return sections
def process_pdf(pdf_path: Path, output_base: Path):
    # Load PDF
    pdf_doc = load_pdf(pdf_path)

    # Extract raw text
    raw_text = extract_raw_text(pdf_doc)

    # Save raw text
    save_raw_text_to_file(raw_text, output_base / "raw_text.txt")

    # Clean text
    cleaned_text = clean_text(raw_text)

    # Save cleaned text
    save_clean_text(cleaned_text, output_base / "cleaned_text.txt")

    # Split into sections
    section_text = split_into_sections(cleaned_text, section_headers)

    # Save sections
    save_sections(section_text, output_base / "sections.json")

#save the split text
def save_sections(sections: dict, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sections, f, indent=2, ensure_ascii=False)
    print(f"split text saved successfully to {output_path}")    
if __name__ == "__main__":
    # Path to sample PDF
    pdf_path = Path(r"text_extraction\sample_paper\test_paper_1.pdf")
    # Load PDF
    pdf_doc = load_pdf(pdf_path)   
    #raw text
    raw_text = extract_raw_text(pdf_doc)
    #preview of the extracted text
    print("\n Raw text preview (first 1000 characters):\n")
    print(raw_text[:1000]) 
    #save raw text to file
    output_file_path = Path("text_extraction/output/raw_text.txt")
    save_raw_text_to_file(raw_text, output_file_path)
    #clean text
    cleaned_text = clean_text(raw_text) 
    #save clean text to a file
    clean_text_path = Path("text_extraction/output/cleaned_text.txt")
    save_clean_text(cleaned_text, clean_text_path)
    #preview of the cleaned text
    print("\n clean text preview (first 1000 characters):\n")
    print(cleaned_text[:1000])
    #text split in sections
    section_text = split_into_sections(cleaned_text,section_headers)
    #save split text
    split_text_path=Path("text_extraction/output/split_text.json")
    save_sections(section_text,split_text_path)
