import os
from typing import TypedDict, Dict, Optional
from langgraph.graph import StateGraph, END

INPUT_DIR = "../week_2/extracted_text"
OUTPUT_DIR = "output_sections"

os.makedirs(OUTPUT_DIR, exist_ok=True)

class PaperState(TypedDict):
    topic: str
    paper: str
    sections: Optional[Dict[str, str]]

def load_sections_node(state: PaperState) -> PaperState:
    topic = state["topic"]
    paper = state["paper"]

    paper_dir = os.path.join(INPUT_DIR, topic, paper)
    sections = {}

    for file in os.listdir(paper_dir):
        if file.endswith(".txt") and not file.startswith("_"):
            sec_name = file.replace(".txt", "")
            with open(os.path.join(paper_dir, file), "r", encoding="utf-8") as f:
                sections[sec_name] = f.read()

    state["sections"] = sections
    return state

def validate_sections_node(state: PaperState) -> PaperState:
    sections = state["sections"]

    if not isinstance(sections, dict):
        raise ValueError("Sections is not a dictionary")

    if len(sections) == 0:
        raise ValueError("No sections found")

    return state

def store_sections_node(state: PaperState) -> PaperState:
    topic = state["topic"]
    paper = state["paper"]
    sections = state["sections"]

    out_dir = os.path.join(OUTPUT_DIR, topic, paper)
    os.makedirs(out_dir, exist_ok=True)

    for sec, content in sections.items():
        with open(os.path.join(out_dir, f"{sec}.txt"), "w", encoding="utf-8") as f:
            f.write(content)

    with open(os.path.join(out_dir, "_summary.txt"), "w", encoding="utf-8") as f:
        f.write("STORED SECTIONS SUMMARY\n")
        f.write("=" * 40 + "\n")
        for sec in sections:
            f.write(f"- {sec}\n")

    return state

graph = StateGraph(PaperState)

graph.add_node("load", load_sections_node)
graph.add_node("validate", validate_sections_node)
graph.add_node("store", store_sections_node)

graph.set_entry_point("load")
graph.add_edge("load", "validate")
graph.add_edge("validate", "store")
graph.add_edge("store", END)

pipeline = graph.compile()

for topic in os.listdir(INPUT_DIR):
    topic_path = os.path.join(INPUT_DIR, topic)
    if not os.path.isdir(topic_path):
        continue

    for paper in os.listdir(topic_path):
        paper_path = os.path.join(topic_path, paper)
        if not os.path.isdir(paper_path):
            continue

        state: PaperState = {
            "topic": topic,
            "paper": paper,
            "sections": None
        }

        pipeline.invoke(state)
        print(f"Processed: {topic}/{paper}")
