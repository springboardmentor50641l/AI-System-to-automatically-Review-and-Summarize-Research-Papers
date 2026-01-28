import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


# -------- DISABLE LANGSMITH --------
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_API_KEY"] = ""


# -------- SECTION ONTOLOGY --------
SECTION_ONTOLOGY = [
    "Abstract",
    "Introduction",
    "Background / Related Work",
    "Methodology",
    "Proposed Solution",
    "Experiments / Results",
    "Conclusion",
    "Limitations",
    "Future Work"
]


# -------- PROMPT TEMPLATE --------
PROMPT_TEMPLATE = """
You are given the full text of a research paper.

Your task is to divide the text into the following logical sections:
{sections}

Rules:
- Do NOT summarize or rephrase the content.
- Do NOT add any new information.
- Assign paragraphs to the most appropriate section based on semantic meaning.
- If a section is missing, return an empty string for that section.
- Return the output strictly as a valid JSON object.

Research Paper Text:
{text}
"""


# -------- SAFE JSON EXTRACTION --------
def _extract_json(text: str) -> dict:
    """
    Safely extract a JSON object from an LLM response.
    Handles extra text or Markdown formatting.
    """
    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == -1:
        raise ValueError("No JSON object found in LLM response")

    json_text = text[start:end]
    return json.loads(json_text)


def semantic_sectioning(text: str, api_key: str) -> dict:
    """
    Use a Large Language Model to semantically divide
    a research paper into logical sections.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0
    )

    prompt = PROMPT_TEMPLATE.format(
        sections=", ".join(SECTION_ONTOLOGY),
        text=text
    )

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    return _extract_json(response.content)
