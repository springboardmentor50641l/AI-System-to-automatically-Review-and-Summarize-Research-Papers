import json
from pathlib import Path
import sys
import os

# Make sure src folder is in Python path
CURRENT_DIR = os.path.dirname(__file__)
sys.path.insert(0, CURRENT_DIR)

from clean_text import clean_text
from section_splitter import split_into_sections, SECTION_HEADERS

# Paths (relative to project root)
PROJECT_ROOT = Path(CURRENT_DIR).parent
RAW_TEXT_PATH = PROJECT_ROOT / "data" / "raw" / "raw_text.txt"
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

# Read raw text
raw_text = RAW_TEXT_PATH.read_text(encoding="utf-8")

# Clean text
cleaned_text = clean_text(raw_text)

# Split into sections
sections = split_into_sections(cleaned_text, SECTION_HEADERS)

# Save sections
(OUTPUT_DIR / "sections.json").write_text(
    json.dumps(sections, indent=2),
    encoding="utf-8"
)

# Save metadata
metadata = {
    "title": "The Impact of Generative AI on Architectural Conceptual Design",
    "sections_extracted": list(sections.keys())
}

(OUTPUT_DIR / "metadata.json").write_text(
    json.dumps(metadata, indent=2),
    encoding="utf-8"
)

print("✅ Project executed successfully")
print("📁 Output saved in output folder")
