import gradio as gr
import traceback
import os
import json
import pandas as pd
from pathlib import Path

# -------- SEARCH + DOWNLOAD --------
from scripts.semantic_search import search_papers
from scripts.download_papers import download_selected_papers, save_metadata

# -------- PIPELINE STAGES --------
from pipeline.run_graph import run_graph_for_topic
from pipeline.analysis.run_analysis import run_analysis_for_topic
from pipeline.analysis.structured_writer import generate_structured_review
from pipeline.analysis.review_module import generate_critique, generate_revision


# -------- PATHS --------
METADATA_PATH = Path("data/metadata/selected_papers_metadata.csv")
SECTIONS_DIR = Path("data/sections")
ANALYSIS_DIR = Path("data/analysis_outputs")


# -------- UTIL --------
def normalize_topic(topic: str):
    return " ".join(topic.lower().split())


def topic_exists_in_metadata(topic: str):
    if not METADATA_PATH.exists():
        return False

    df = pd.read_csv(METADATA_PATH)
    df["topic_norm"] = df["topic"].astype(str).apply(normalize_topic)
    return normalize_topic(topic) in df["topic_norm"].values


def structured_review_exists(topic: str):
    path = ANALYSIS_DIR / f"{topic.replace(' ', '_')}_final_review.txt"
    return path.exists()


def analytical_draft_exists(topic: str):
    path = ANALYSIS_DIR / f"{topic.replace(' ', '_')}_analytical_draft.txt"
    return path.exists()


def sections_exist_for_topic(topic: str):
    if not METADATA_PATH.exists():
        return False

    df = pd.read_csv(METADATA_PATH)
    df["topic_norm"] = df["topic"].astype(str).apply(normalize_topic)
    topic_df = df[df["topic_norm"] == normalize_topic(topic)]

    if topic_df.empty:
        return False

    for pdf_path in topic_df["pdf_path"]:
        if not isinstance(pdf_path, str):
            continue

        stem = Path(pdf_path).stem
        section_file = SECTIONS_DIR / f"{stem}_sections_langgraph.json"
        if not section_file.exists():
            return False

    return True


# -------- FULL PIPELINE --------
def run_full_pipeline(topic):
    logs = []

    try:
        if not topic or not topic.strip():
            yield "Enter a topic.", ""
            return

        topic = topic.strip()
        topic_norm = normalize_topic(topic)

        # -------- SEARCH + DOWNLOAD --------
        if topic_exists_in_metadata(topic):
            logs.append("Topic found in existing metadata.")
            logs.append("Skipping search and download.")
        else:
            logs.append("Searching papers...")
            yield "  \n".join(logs), ""


            papers = search_papers(topic)
            logs.append(f"Found {len(papers)} papers.")
            yield "  \n".join(logs), ""


            logs.append("Downloading PDFs...")
            yield "  \n".join(logs), ""

            download_selected_papers(papers)
            save_metadata(papers)

            logs.append("Download complete.")
            yield "  \n".join(logs), ""

        # -------- LANGGRAPH --------
        if sections_exist_for_topic(topic):
            logs.append("Existing section files detected.")
            logs.append("Skipping LangGraph processing.")
        else:
            logs.append("Running LangGraph sectioning...")
            yield "\n".join(logs), ""

            def graph_cb(msg):
                logs.append(msg)

            run_graph_for_topic(topic, progress_callback=graph_cb)

        yield "  \n".join(logs), ""


        # -------- ANALYSIS --------
        if analytical_draft_exists(topic):
            logs.append("Analytical draft already exists.")
            logs.append("Skipping analysis stage.")
        else:
            logs.append("Running analysis stage...")
            yield "  \n".join(logs), ""


            def analysis_cb(msg):
                logs.append(msg)

            run_analysis_for_topic(topic, progress_callback=analysis_cb)

        yield "  \n".join(logs), ""


        # -------- STRUCTURED WRITER --------
        if structured_review_exists(topic):
            logs.append("Structured review already exists.")
            logs.append("Loading existing review...")
            review_path = ANALYSIS_DIR / f"{topic.replace(' ', '_')}_final_review.txt"
            final_review = review_path.read_text(encoding="utf-8")
        else:
            logs.append("Generating structured review...")
            yield "  \n".join(logs), ""


            def structured_cb(msg):
                logs.append(msg)

            final_review = generate_structured_review(
                topic,
                progress_callback=structured_cb
            )

        logs.append("Pipeline completed.")
        yield "  \n".join(logs), final_review

    except Exception as e:
        yield f"Error:\n{str(e)}\n\n{traceback.format_exc()}", ""


# -------- CRITIQUE --------
def critique_pipeline(topic):
    try:
        return generate_critique(topic)
    except Exception as e:
        return f"Error:\n{str(e)}"


# -------- REVISION --------
def revision_pipeline(topic):
    try:
        return generate_revision(topic)
    except Exception as e:
        return f"Error:\n{str(e)}"


# -------- CSS --------
custom_css = """
body {
    background: radial-gradient(circle at 50% 0%, #111111, #000000 60%);
    color: #ffffff;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.gradio-container {
    padding: 40px 80px !important;
}

.hero-title {
    font-size: 72px;
    font-weight: 800;
    text-align: center;
    color: #ffffff;
    letter-spacing: -1px;
    margin-bottom: 12px;
}

.hero-sub {
    text-align: center;
    color: #b3b3b3;
    margin-bottom: 40px;
    font-weight: 500;
}

input, textarea {
    background-color: #0a0a0a !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 8px !important;
}

button {
    background-color: #000000 !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    color: #ffffff !important;
    border-radius: 6px !important;
    box-shadow: 0 0 8px rgba(255,255,255,0.25);
    transition: all 0.2s ease;
}

button:hover {
    box-shadow: 0 0 12px rgba(255,255,255,0.35);
}

.markdown-box {
    background-color: #0b0b0b !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    padding: 18px !important;
    border-radius: 8px !important;
    height: 500px;
    overflow-y: auto;
}

h3 {
    margin-bottom: 6px !important;
    margin-top: 15px !important;
}

footer {
    display: none !important;
}
"""



# -------- BUILD UI --------
with gr.Blocks() as app:


    gr.HTML("""
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    """)

    gr.HTML("<div class='hero-title'>AI Research Review System</div>")
    gr.HTML("<div class='hero-sub'>Intelligent Automated Literature Synthesis Engine</div>")

    topic_input = gr.Textbox(
        placeholder="Enter research topic...",
        label=None
    )

    run_button = gr.Button("Run Full Pipeline")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Live Pipeline Status")
            status_box = gr.Markdown(elem_classes="markdown-box")

        with gr.Column():
            gr.Markdown("### Final Structured Review")
            output_box = gr.Markdown(elem_classes="markdown-box")

    gr.Markdown("## Review & Refinement")

    with gr.Row():
        critique_button = gr.Button("Generate Critique")
        revision_button = gr.Button("Generate Revision")

    with gr.Row():
        critique_output = gr.Markdown(elem_classes="markdown-box")
        revision_output = gr.Markdown(elem_classes="markdown-box")

    run_button.click(
        run_full_pipeline,
        inputs=topic_input,
        outputs=[status_box, output_box]
    )

    critique_button.click(
        critique_pipeline,
        inputs=topic_input,
        outputs=critique_output
    )

    revision_button.click(
        revision_pipeline,
        inputs=topic_input,
        outputs=revision_output
    )


app.launch(css=custom_css)

