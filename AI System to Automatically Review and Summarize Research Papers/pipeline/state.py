from typing import TypedDict, Optional


class PaperState(TypedDict):
    pdf_path: str
    raw_text: Optional[str]
    normalized_text: Optional[str]
    sections: Optional[dict]
