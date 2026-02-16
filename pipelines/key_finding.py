
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import json
import re
from pathlib import Path


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",timeout=120,temperature=0)

#Strict JSON extraction and validation helper.
def extract_json(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model output")
    return match.group(0)

def has_required_sections(sections: dict) -> bool:
    required = ["abstract", "methodology", "results"]

    for r in required:
        content = sections.get(r, "")
        if not isinstance(content, str) or not content.strip():
            return False

    return True
def generate_comparison_id() -> str:
    return datetime.now().strftime("comparison_%Y%m%d_%H%M%S")
def load_paper_data(paper_id: str):
    base_dir = Path("text_extraction/output")

    section_path = base_dir / "sectioned_data" / f"sectioned_data_{paper_id}.json"
    clean_path = base_dir / "clean_text" / f"clean_text_{paper_id}.txt"

    if not section_path.exists():
        raise FileNotFoundError(f"Sections file not found: {section_path}")

    if not clean_path.exists():
        raise FileNotFoundError(f"Clean text file not found: {clean_path}")

    with open(section_path, "r", encoding="utf-8") as f:
        sections = json.load(f)

    with open(clean_path, "r", encoding="utf-8") as f:
        clean_text = f.read()

    return sections, clean_text

#key findings
def extract_key_findings(sections: dict, clean_text: str, llm) -> dict:

    # Decide data source
    if has_required_sections(sections):
        print("[INFO] Using semantic sections for key findings")

        source_data = {
            k: v
            for k, v in sections.items()
            if isinstance(v, str) and v.strip()
        }

    else:
        print("[INFO] Required sections missing — falling back to clean_text")

        if not clean_text or not clean_text.strip():
            raise ValueError("No clean_text available for fallback")

        source_data = {"full_text": clean_text}

    prompt = f"""
    You are an expert research analyst.

    Extract ALL major findings and main contributions explicitly stated in the text.

    Rules:
    - Use ONLY the given content
    - Do NOT add external knowledge
    - Do NOT infer beyond the text
    - Be concise and factual
    - Return STRICT JSON only (no commentary)

    Each finding must include:
    - claim
    - evidence
    - source_section
    - limitations (empty if none explicitly stated)

    Text:
    {json.dumps(source_data, indent=2)}

    Output format:
    {{
      "key_findings": [
        {{
          "claim": "",
          "evidence": "",
          "source_section": "",
          "limitations": ""
        }}
      ]
    }}
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    raw = response.content if hasattr(response, "content") else response

    if not raw or not raw.strip():
        return {"key_findings": []}

    try:
        cleaned = extract_json(raw)
        return json.loads(cleaned)
    except Exception:
        return {
            "error": "Failed to parse key findings JSON",
            "raw_output": raw
        }

def run_key_findings(paper_id: str, comparison_id: str):
    sections, clean_text = load_paper_data(paper_id)

    key_findings = extract_key_findings(
        sections=sections,
        clean_text=clean_text,
        llm=llm
    )

    store_key_findings(key_findings, paper_id, comparison_id)


from pathlib import Path
import json

def store_key_findings(result: dict, paper_id: str, comparison_id: str) -> Path:
    base_dir = Path("text_extraction/output/key_findings")
    output_dir = base_dir / comparison_id
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"key_findings_{paper_id}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


    print(f"[OK] Key findings saved to {output_path}")
    return output_path





if __name__ == "__main__":

    paper_id = "20260214_041031_718557"

    comparison_id = generate_comparison_id()

    run_key_findings(paper_id, comparison_id)
