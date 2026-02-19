import os
from pathlib import Path
from typing import Callable, Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_TRACING"] = "false"

load_dotenv()

# ---------------- CONFIG ----------------
ANALYSIS_DIR = Path("data/analysis_outputs")


# ---------------- LLM ----------------
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0
    )


# ---------------- LOAD REVIEW ----------------
def load_final_review(topic: str) -> str:
    filename = topic.replace(" ", "_") + "_final_review.txt"
    path = ANALYSIS_DIR / filename

    if not path.exists():
        raise FileNotFoundError("Final structured review not found.")

    return path.read_text(encoding="utf-8")


# ---------------- CRITIQUE ----------------
def generate_critique(
    topic: str,
    progress_callback: Optional[Callable[[str], None]] = None,
    review_text: Optional[str] = None
) -> str:

    if review_text is None:
        review_text = load_final_review(topic)

    if progress_callback:
        progress_callback("Generating critique")

    llm = get_llm()

    prompt = f"""
You are an academic reviewer.

Critically evaluate the following research review.

Assess:
- Clarity and coherence
- Logical flow
- Repetition
- Strength of synthesis
- Academic tone
- Structural consistency

Return:
- Bullet-point critique
- Specific improvement suggestions
- Do NOT rewrite the draft
- No extra commentary

Review:
{review_text}
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    critique = response.content.strip()

    critique_file = ANALYSIS_DIR / f"{topic.replace(' ', '_')}_critique.txt"
    critique_file.write_text(critique, encoding="utf-8")

    if progress_callback:
        progress_callback("Critique generated successfully")

    return critique


# ---------------- REVISION ----------------
def generate_revision(
    topic: str,
    progress_callback: Optional[Callable[[str], None]] = None,
    review_text: Optional[str] = None,
    critique_text: Optional[str] = None
) -> str:

    if review_text is None:
        review_text = load_final_review(topic)

    if critique_text is None:
        critique_file = ANALYSIS_DIR / f"{topic.replace(' ', '_')}_critique.txt"
        if critique_file.exists():
            critique_text = critique_file.read_text(encoding="utf-8")
        else:
            critique_text = generate_critique(topic, review_text=review_text)

    if progress_callback:
        progress_callback("Generating revised draft")

    llm = get_llm()

    prompt = f"""
You are an academic editor.

Revise the following research review based on the critique provided.

Goals:
- Improve clarity
- Remove redundancy
- Strengthen logical flow
- Maintain academic tone
- Preserve original meaning
- Do NOT add external information

Critique:
{critique_text}

Original Review:
{review_text}
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    revised = response.content.strip()

    revised_file = ANALYSIS_DIR / f"{topic.replace(' ', '_')}_revised_review.txt"
    revised_file.write_text(revised, encoding="utf-8")

    if progress_callback:
        progress_callback("Revised draft generated successfully")

    return revised


# ---------------- CLI MODE ----------------
def main():
    topic = input("Enter topic for review cycle: ").strip()
    if not topic:
        print("Topic cannot be empty.")
        return

    critique = generate_critique(topic, print)

    choice = input("Generate revised version? (y/n): ").strip().lower()

    if choice == "y":
        generate_revision(topic, print)


if __name__ == "__main__":
    main()
