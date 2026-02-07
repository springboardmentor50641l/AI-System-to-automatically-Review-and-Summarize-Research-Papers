from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from datetime import datetime
from pathlib import Path
import re
    
import json

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",timeout=120,temperature=0)


#final draft
def generate_draft(comparison: dict, llm) -> str:
    formatted_comparison = json.dumps(comparison, indent=2)

    prompt = f"""
    You are an academic writing assistant.

    Using ONLY the structured comparative analysis provided below,
    write a coherent literature review section.

    Requirements:
    - Formal academic tone
    - Clear paragraph structure
    - Objective and neutral language
    - No external knowledge
    - No hallucinated citations
    - Do NOT introduce new comparisons or interpretations
    - Base all statements strictly on the provided comparison

    Comparative Analysis:
    {formatted_comparison}

    Write the literature review section now.
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content
#store draft
def store_literature_review(review_text: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = output_dir / f"literature_review_{timestamp}.txt"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(review_text)

    return file_path

if __name__ == "__main__":
    comparison_file = Path("text_extraction/output/review_comparison/review_comparison_20260207_100819.json")

with comparison_file.open("r", encoding="utf-8") as f:
    comparison_data = json.load(f)

    # Generate draft
    literature_review = generate_draft(comparison_data, llm)

    # Store result
    output_path = store_literature_review(
        literature_review,
        output_dir=Path(r"text_extraction\output\draft"))

    print(f"Literature review saved at: {output_path}")