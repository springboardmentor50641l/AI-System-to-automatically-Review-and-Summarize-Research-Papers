from typing import TypedDict, Optional, Dict, List


class PaperState(TypedDict, total=False):
    pdf_path: str
    raw_text: Optional[str]
    clean_text: Optional[str]
    sections: Optional[Dict]
    output_path: Optional[str]
    current_folder: Optional[str]
    
    all_papers_sections: Optional[List[Dict]]
    aggregated_content: Optional[Dict]
    processed_papers: Optional[List[Dict]]
    comparison_text: Optional[str]

    review_draft: Optional[str]
    critique_feedback: Optional[str]
    final_review: Optional[str]
