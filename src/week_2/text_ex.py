import pymupdf4llm
import re
import os

PDF_BASE_DIR = "../week_1/pdfs"
OUTPUT_BASE_DIR = "extracted_text"

os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)

sections = [
    "abstract",
    "introduction",
    "literature review",
    "related work",
    "methodology",
    "methods",
    "experimental setup",
    "results",
    "discussion",
    "conclusion",
    "references"
]

def normalize_text(text: str) -> str:
    text = text.replace("-\n", "")
    text = text.replace("\r", "")
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()

SECTION_PATTERN = re.compile(
    r"\*\*\s*(\d+\.|[ivx]+\.)?\s*(abstract|introduction|literature review|related work|methodology|methods|experimental setup|results|discussion|conclusion|references)\s*\*\*",
    re.IGNORECASE
)

PLAIN_SECTION_PATTERN = re.compile(
    r"^\s*(\d+\.|[ivx]+\.)?\s*(abstract|introduction|literature review|related work|methodology|methods|experimental setup|results|discussion|conclusion|references)\s*[:\-\.]?\s*$",
    re.IGNORECASE
)

def extract_sections_from_pdf(pdf_path, output_folder):
    print(f"\n📄 Processing: {pdf_path}")

    raw_text = pymupdf4llm.to_markdown(pdf_path)
    clean_text = normalize_text(raw_text)
    lines = clean_text.split("\n")

    with open(os.path.join(output_folder, "raw_text.txt"), "w", encoding="utf-8") as f:
        f.write(clean_text)

    found_headers = []

    for i, line in enumerate(lines):
        for match in SECTION_PATTERN.finditer(line):
            sec = match.group(2).lower()
            found_headers.append((sec, i))

        if PLAIN_SECTION_PATTERN.match(line.strip()):
            sec = PLAIN_SECTION_PATTERN.match(line.strip()).group(2).lower()
            found_headers.append((sec, i))

    found_headers = list(dict.fromkeys(found_headers))
    found_headers.sort(key=lambda x: x[1])

    if not found_headers:
        print("❌ No headers detected")
        return

    section_text = {}

    for idx, (sec, start_line) in enumerate(found_headers):
        if idx + 1 < len(found_headers):
            end_line = found_headers[idx + 1][1]
        else:
            end_line = len(lines)

        content_lines = lines[start_line + 1:end_line]
        content = "\n".join(content_lines).strip()
        content = content.lstrip("—:-.\n\t ")

        if len(content) > 150:
            section_text[sec] = content

    if section_text:
        for sec, content in section_text.items():
            filename = sec.replace(" ", "_") + ".txt"
            with open(os.path.join(output_folder, filename), "w", encoding="utf-8") as f:
                f.write(content)

        with open(os.path.join(output_folder, "_summary.txt"), "w", encoding="utf-8") as f:
            f.write("EXTRACTED SECTIONS SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            for sec in section_text:
                f.write(f"{sec.upper()}: {len(section_text[sec]):,} chars\n")

        print(f"✅ Extracted {len(section_text)} sections:", list(section_text.keys()))
    else:
        print("❌ Headers found but no content extracted")

for topic in os.listdir(PDF_BASE_DIR):
    topic_path = os.path.join(PDF_BASE_DIR, topic)

    if not os.path.isdir(topic_path):
        continue

    for pdf_file in os.listdir(topic_path):
        if not pdf_file.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(topic_path, pdf_file)

        paper_name = pdf_file.replace(".pdf", "")
        output_folder = os.path.join(OUTPUT_BASE_DIR, topic, paper_name)
        os.makedirs(output_folder, exist_ok=True)

        if os.path.exists(os.path.join(output_folder, "_summary.txt")):
            print(f"⏭ Skipping (already extracted): {pdf_path}")
            continue

        extract_sections_from_pdf(pdf_path, output_folder)
