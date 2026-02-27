import json
import glob
from langchain_core.messages import HumanMessage
from graph.llm_config import llm


# ---------------- AGGREGATE ----------------
def aggregate_node(state):
    folder = state.get("current_folder")

    section_files = glob.glob(f"{folder}/*_sections.json")

    all_sections = []

    for file in section_files:
        with open(file, "r", encoding="utf-8") as f:
            all_sections.append(json.load(f))

    state["all_papers_sections"] = all_sections
    return state


# ---------------- KEY FINDINGS ----------------
def key_findings_node(state):
    papers = state.get("all_papers_sections", [])
    processed = []

    for paper in papers:
        prompt = f"""
Extract key findings and main contributions
from the following research paper sections.

Rules:
- Use only provided content
- Return bullet points
- Do not hallucinate

Sections:
{paper}
"""
        response = llm.invoke([HumanMessage(content=prompt)])

        processed.append({
            "sections": paper,
            "key_findings": response.content
        })

    state["processed_papers"] = processed
    return state


# ---------------- COMPARISON ----------------
def comparison_node(state):
    processed = state.get("processed_papers", [])

    findings = [p["key_findings"] for p in processed]

    prompt = f"""
You are conducting a comparative literature review.

Compare the following extracted findings.

Tasks:
- Identify common themes
- Highlight differences
- Mention strengths and limitations
- Identify research gaps

Findings:
{findings}

Return structured academic comparison.
"""
    response = llm.invoke([HumanMessage(content=prompt)])

    state["comparison_text"] = response.content
    return state


# ---------------- DRAFT REVIEW ----------------
def draft_review_node(state):
    comparison = state.get("comparison_text", "")

    prompt = f"""
Using the following comparative analysis,
write a structured academic literature review draft.

Structure:
- Introduction
- Thematic Analysis
- Research Gaps
- Conclusion

Comparative Analysis:
{comparison}
"""
    response = llm.invoke([HumanMessage(content=prompt)])

    state["review_draft"] = response.content
    return state


# ---------------- CRITIQUE ----------------
def critique_node(state):
    draft = state.get("review_draft", "")

    prompt = f"""
Act as a journal reviewer.

Critically evaluate this literature review.

Assess:
- Clarity
- Coherence
- Logical flow
- Academic tone
- Strength of synthesis

Return bullet-point critique only.

Review:
{draft}
"""
    response = llm.invoke([HumanMessage(content=prompt)])

    state["critique_feedback"] = response.content
    return state


# ---------------- FINAL REVISION ----------------
def revise_node(state):
    draft = state.get("review_draft", "")
    critique = state.get("critique_feedback", "")

    prompt = f"""
Revise the literature review using the critique below.

Maintain original meaning.
Improve clarity, flow, and structure.

Review:
{draft}

Critique:
{critique}
"""
    response = llm.invoke([HumanMessage(content=prompt)])

    state["final_review"] = response.content
    return state