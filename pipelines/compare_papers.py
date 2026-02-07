from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from datetime import datetime
from pathlib import Path
import re
    
import json

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",timeout=120,temperature=0)


#Strict JSON extraction and validation helper.
def extract_json_strict(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("Empty LLM output")

    text = text.strip()

    # remove markdown fences
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found")

    return json.loads(match.group(0))

#load multiple papers
def load_all_key_findings(key_findings_dir: Path) -> list:
    """
    Loads all key finding JSON files into a unified list.
    """

    papers = []

    for file in key_findings_dir.glob("key_findings_*.json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        paper_id = file.stem.replace("key_findings_", "")

        papers.append({
            "paper_id": paper_id,
            "key_findings": data.get("key_findings", [])
        })

    if len(papers) < 2:
        raise ValueError("At least two papers are required for comparison")

    return papers


#compare key findings
def compare_all_key_findings(papers: list, llm) -> dict:
    """
    Compares key findings across multiple papers and produces
    review-style claim clusters.
    """

    prompt = f"""
    You are an expert research reviewer writing a literature review.

    You are given key findings from multiple research papers.

    Your task:
    - Group semantically similar claims together
    - Identify consensus and divergence
    - Track which papers support which claims

    Rules:
    - Use ONLY the provided content
    - Do NOT add external knowledge
    - Do NOT merge unrelated claims
    - Be conservative in clustering
    - Return STRICT JSON only

    Input papers:
    {json.dumps(papers, indent=2)}

    Return JSON in the following format:

    {{
    "claim_clusters": [
        {{
        "cluster_claim": "",
        "supported_by_papers": [
            {{
            "paper_id": "",
            "evidence": ""
            }}
        ],
        "limitations": ""
        }}
    ],
    "unique_claims": [
        {{
        "claim": "",
        "paper_id": "",
        "evidence": ""
        }}
    ]
    }}
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    raw_output = response.content

    try:
        parsed = extract_json_strict(raw_output)
    except Exception as e:
        return {
            "error": "Failed to parse multi-paper comparison JSON",
            "exception": str(e),
            "raw_output": raw_output
        }

    return parsed

#store comparision
def store_review_comparison(result: dict) -> Path:
    output_dir = Path("text_extraction/output/review_comparison")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"review_comparison_{timestamp}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"[OK] Review comparison saved to {output_path}")
    return output_path


if __name__ == "__main__":
    key_findings_dir = Path("text_extraction/output/key_findings")

    papers = load_all_key_findings(key_findings_dir)

    review_comparison = compare_all_key_findings(
        papers=papers,
        llm=llm)

    store_review_comparison(review_comparison)

    print(json.dumps(review_comparison, indent=2))