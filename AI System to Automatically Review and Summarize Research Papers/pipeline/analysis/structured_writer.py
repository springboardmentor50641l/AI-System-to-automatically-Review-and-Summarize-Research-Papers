from pathlib import Path
import json
import pandas as pd
import os
from typing import Callable, Optional

os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_TRACING"] = "false"

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

# ---------------- CONFIG ----------------
ANALYSIS_DIR = Path("data/analysis_outputs")
SECTIONS_DIR = Path("data/sections")
METADATA_PATH = Path("data/metadata/selected_papers_metadata.csv")

OUTPUT_DIR = Path("data/analysis_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


# ---------------- LLM ----------------
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0
    )


# ---------------- UTIL ----------------
def normalize_topic(topic: str) -> str:
    return " ".join(topic.lower().split())


def load_analytical_draft(topic: str) -> str:
    filename = topic.replace(" ", "_") + "_analytical_draft.txt"
    path = ANALYSIS_DIR / filename

    if not path.exists():
        raise FileNotFoundError("Analytical draft not found. Run analysis stage first.")

    return path.read_text(encoding="utf-8")


def load_metadata_for_topic(topic: str):
    if not METADATA_PATH.exists():
        raise FileNotFoundError("Metadata file not found.")

    df = pd.read_csv(METADATA_PATH)
    df["topic_norm"] = df["topic"].astype(str).apply(normalize_topic)

    topic_norm = normalize_topic(topic)
    return df[df["topic_norm"] == topic_norm]


def load_methods_sections(topic_df):
    methods_texts = []

    for pdf_path in topic_df["pdf_path"]:
        if not isinstance(pdf_path, str):
            continue

        stem = Path(pdf_path).stem
        section_file = SECTIONS_DIR / f"{stem}_sections_langgraph.json"

        if section_file.exists():
            with open(section_file, "r", encoding="utf-8") as f:
                sections = json.load(f)

            method_text = sections.get("Methodology", "")
            if method_text.strip():
                methods_texts.append(method_text)

    return methods_texts


# ---------------- ABSTRACT ----------------
def generate_abstract(topic: str, analytical_draft: str) -> str:
    llm = get_llm()

    prompt = f"""
Write a concise academic abstract (maximum 100 words) for the following research review.

Topic:
{topic}

Content:
{analytical_draft}

Rules:
- Maximum 100 words
- Academic tone
- Do not mention specific paper titles
- No citations
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()


# ---------------- METHODS ----------------
def generate_methods_section(methods_texts: list) -> str:
    if len(methods_texts) == 1:
        return f"### Methodology Overview\n\n{methods_texts[0].strip()}"

    llm = get_llm()

    prompt = f"""
Compare the following methodology sections from multiple research papers.

Tasks:
- Identify similarities
- Highlight differences
- Describe research approaches used

Rules:
- Academic tone
- Do not mention paper titles
- Do not add external knowledge

Method Sections:
{json.dumps(methods_texts, indent=2)}
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return "### Methods Comparison\n\n" + response.content.strip()


# ---------------- RESULTS ----------------
def generate_results_section(analytical_draft: str) -> str:
    llm = get_llm()

    prompt = f"""
From the following analytical draft, extract and rewrite only the results synthesis section.

Focus on:
- Comparative findings
- Key outcomes
- Observed patterns

Rules:
- Academic tone
- Do not repeat background content
- Do not mention paper titles

Draft:
{analytical_draft}
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return "### Results Synthesis\n\n" + response.content.strip()


# ---------------- APA REFERENCES ----------------
def generate_apa_references(topic_df) -> str:
    llm = get_llm()

    papers_text = ""

    for _, row in topic_df.iterrows():
        papers_text += f"""
Paper:
Title: {row.get('title')}
Authors: {row.get('authors')}
Year: {row.get('year')}
Venue: {row.get('venue')}
DOI: {row.get('doi')}
"""

    prompt = f"""
Format the following papers in APA 7th edition reference style.

Rules:
- Return references only
- One reference per line
- No explanations

{papers_text}
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return "### References\n\n" + response.content.strip()


# ---------------- MAIN STRUCTURED FUNCTION ----------------
def generate_structured_review(
    topic: str,
    progress_callback: Optional[Callable[[str], None]] = None
):
    topic_df = load_metadata_for_topic(topic)

    if topic_df.empty:
        raise ValueError("No metadata found for this topic.")

    analytical_draft = load_analytical_draft(topic)

    if progress_callback:
        progress_callback("Generating Abstract")
    abstract = generate_abstract(topic, analytical_draft)

    if progress_callback:
        progress_callback("Generating Methods Section")
    methods_texts = load_methods_sections(topic_df)
    methods_section = generate_methods_section(methods_texts)

    if progress_callback:
        progress_callback("Generating Results Section")
    results_section = generate_results_section(analytical_draft)

    if progress_callback:
        progress_callback("Generating APA References")
    references = generate_apa_references(topic_df)

    final_output = f"""
### Abstract

{abstract}

{methods_section}

{results_section}

{references}
"""

    output_file = OUTPUT_DIR / f"{topic.replace(' ', '_')}_final_review.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_output.strip())

    if progress_callback:
        progress_callback("Structured review generated successfully")

    return final_output.strip()


# ---------------- CLI MODE ----------------
def main():
    topic = input("Enter topic for structured writing: ").strip()
    if not topic:
        print("Topic cannot be empty.")
        return

    generate_structured_review(topic, print)


if __name__ == "__main__":
    main()
