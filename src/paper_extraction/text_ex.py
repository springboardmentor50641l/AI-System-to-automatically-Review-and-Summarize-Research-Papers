import pymupdf4llm
import re
import os

pdf_path = "research_paper.pdf"

# ---------- Extract raw text ----------
raw_text = pymupdf4llm.to_markdown(pdf_path)
text_lower = raw_text.replace("\r", "").lower()
text_original = raw_text.replace("\r", "")

with open("raw_text.txt", "w", encoding="utf-8") as f:
    f.write(raw_text)

print(f"Text length: {len(text_lower):,} characters")

# ---------- Section markers ----------
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

# ---------- Find section positions ----------
positions = []

for sec in sections:
    # Look for the section in various formats
    patterns = [
        f"^{sec}$",  # "abstract" on its own line
        f"\\d+\\.\\s*{sec}",  # "1. introduction"
        f"[ivx]+\\.\\s*{sec}",  # "i. introduction"
        f"^{sec}\\s*[:.-]",  # "abstract:" or "abstract -"
    ]
    
    # Search line by line for better accuracy
    lines = text_lower.split('\n')
    for line_num, line in enumerate(lines):
        line = line.strip()
        for pattern in patterns:
            if re.search(pattern, line):
                # Found the section header
                start_pos = sum(len(l) + 1 for l in lines[:line_num])  # Calculate position
                positions.append((sec, start_pos, line_num, line))
                print(f"✓ Found '{sec}' at line {line_num}: '{line}'")
                break
        if any(pos[0] == sec for pos in positions):  # Stop after finding first occurrence
            break

# Sort by position
positions.sort(key=lambda x: x[1])

print(f"\nFound {len(positions)} sections")

# ---------- Extract clean section text ----------
section_text = {}

for i, (sec, start_pos, line_num, header_found) in enumerate(positions):
    # Find end position (start of next section or end of text)
    if i + 1 < len(positions):
        end_line_num = positions[i + 1][2]
        # Get text from line after current header to line before next header
        lines = text_original.split('\n')
        content_lines = []
        for j in range(line_num + 1, end_line_num):
            # Skip if this line is another section header
            line_lower = lines[j].lower().strip()
            is_other_header = False
            for other_sec in sections:
                if other_sec != sec:
                    if any(pattern in line_lower for pattern in [
                        f"^{other_sec}$",
                        f"\\d+\\.\\s*{other_sec}",
                        f"{other_sec}\\s*[:.-]"
                    ]):
                        is_other_header = True
                        break
            if not is_other_header:
                content_lines.append(lines[j])
        
        content = '\n'.join(content_lines).strip()
    else:
        # Last section - take everything after
        lines = text_original.split('\n')
        content_lines = []
        for j in range(line_num + 1, len(lines)):
            content_lines.append(lines[j])
        content = '\n'.join(content_lines).strip()
    
    # Clean up: remove leading special characters
    content = content.lstrip("—:-.\n\t ")
    
    # Only save if we have content
    if content and len(content) > 100:
        section_text[sec] = content
        print(f"✓ Extracted '{sec}' ({len(content):,} chars)")

# ---------- Save sections ----------
if section_text:
    os.makedirs("sections", exist_ok=True)
    
    for sec, content in section_text.items():
        filename = sec.replace(" ", "_") + ".txt"
        with open(os.path.join("sections", filename), "w", encoding="utf-8") as f:
            f.write(content)
    
    print(f"\n✅ Extracted {len(section_text)} sections:", list(section_text.keys()))
    
    # Also save a summary
    with open("sections/_summary.txt", "w", encoding="utf-8") as f:
        f.write("EXTRACTED SECTIONS SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        for sec in sorted(section_text.keys()):
            f.write(f"{sec.upper()}:\n")
            f.write(f"  Size: {len(section_text[sec]):,} characters\n")
            f.write(f"  Lines: {section_text[sec].count(chr(10)) + 1:,}\n")
            f.write("-" * 40 + "\n")
    
    print("Summary saved to: sections/_summary.txt")
else:
    print("\n❌ No sections could be extracted!")