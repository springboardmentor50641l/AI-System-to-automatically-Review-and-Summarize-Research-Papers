# List of expected research paper headings
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

def split_into_sections(text, headers):
    """
    Splits text into sections based on headers
    """
    sections = {}
    current_section = "Preamble"
    sections[current_section] = []

    # Split text line by line
    lines = text.split("\n")

    for line in lines:
        line_clean = line.strip()

        is_header = False
        for header in headers:
            if line_clean.lower() == header.lower():
                current_section = header
                sections[current_section] = []
                is_header = True
                break

        # Add line to current section
        if not is_header:
            sections[current_section].append(line)

    # Join lines into paragraphs
    for key in sections:
        sections[key] = "\n".join(sections[key]).strip()

    return sections
