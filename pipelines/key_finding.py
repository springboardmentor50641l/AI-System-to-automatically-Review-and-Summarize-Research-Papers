
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


#key findings
def extract_key_findings(sections: dict, llm) -> dict:

    # Filter out empty sections
    filtered_sections = {
        k: v for k, v in sections.items()
        if isinstance(v, str) and v.strip()}

    if not filtered_sections:
        raise ValueError("No usable sections available for key findings extraction")

    prompt = f"""
    You are an expert research analyst.

    From the following research paper sections, extract the key findings
    and main contributions made by the authors.

    Rules:
    - Use ONLY the given content
    - Do NOT add external knowledge
    - Do NOT infer beyond the text
    - Each finding must be explicitly supported by the paper
    - Be concise and factual
    - Return STRICT JSON only (no commentary, no markdown)

    Each finding must include:
    1. claim
    2. supporting evidence
    3. source section
    4. limitations (only if explicitly mentioned, otherwise empty string)

    Sections:
    {json.dumps(filtered_sections, indent=2)}

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

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    raw = response.content if hasattr(response, "content") else response

    if not raw or not raw.strip():
        return {"key_findings": []}

    try:
        cleaned = extract_json(raw)
        return json.loads(cleaned)
    except Exception as e:
        # Fail soft, not silent
        return {
            "error": "Failed to parse key findings JSON",
            "raw_output": raw
        }

def store_key_findings(key_findings: dict, paper_id: str) -> Path:
   #Stores key findings in a uniquely named JSON file.


    output_dir = Path("text_extraction/output/key_findings")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"key_findings_{paper_id}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(key_findings, f, indent=2, ensure_ascii=False)

    print(f"[OK] Key findings stored at: {output_path}")
    return output_path



if __name__ == "__main__":
    section_file = Path(r"C:\Users\Pari\Desktop\AI-System-to-automatically-Review-and-Summarize-Research-Papers\text_extraction\output\sectioned_data_20260207_091522_789269.json")

    if not section_file.exists():
        raise FileNotFoundError(f"Section file not found: {section_file}")

    with open(section_file, "r", encoding="utf-8") as f:
        sections = json.load(f)

    # Extract key findings
    key_findings = extract_key_findings(sections, llm)

    # Store results
    store_key_findings(
        key_findings=key_findings,
        paper_id=section_file.stem.replace("sectioned_data_", ""))

    # Debug print (optional)
    print(json.dumps(key_findings, indent=2))    