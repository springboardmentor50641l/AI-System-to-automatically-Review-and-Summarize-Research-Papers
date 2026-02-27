import gradio as gr
import os
from main import sanitize_topic
from search import search_papers
from download import select_and_download_pdfs
from dataset import prepare_dataset
from graph.pipeline import build_extraction_pipeline, build_review_pipeline
from dotenv import load_dotenv

load_dotenv()


def run_system(topic):
    api_key = os.getenv("CORE_API_KEY")

    safe_topic = sanitize_topic(topic)
    folder = os.path.join("papers", safe_topic)

    papers = search_papers(topic, api_key)
    downloaded, _ = select_and_download_pdfs(papers, 3, folder)

    if not downloaded:
        return "No papers found.", "", ""

    extraction_pipeline = build_extraction_pipeline()

    for pdf in downloaded:
        extraction_pipeline.invoke({"pdf_path": pdf})

    review_pipeline = build_review_pipeline()
    state_input = {"current_folder": folder}

    final_state = review_pipeline.invoke(state_input)

    comparison = final_state.get("comparison_text", "")
    draft = final_state.get("review_draft", "")
    final = final_state.get("final_review", "")

    review_path = os.path.join(folder, "final_literature_review.txt")

    with open(review_path, "w", encoding="utf-8") as f:
        f.write(final)

    return comparison, draft, final


custom_theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="indigo",
).set(
    body_background_fill="#f8fafc",
    block_background_fill="white",
    block_radius="12px",
)


with gr.Blocks(
    theme=custom_theme,
    css="""
.gradio-container {
    max-width: 100% !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}

.hero {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 0 30px 0;
    text-align: center;
}

.hero h1 {
    font-size: 42px;
    font-weight: 800;
    margin: 0;
}

.hero p {
    font-size: 18px;
    color: #9ca3af;
    margin-top: 10px;
}

#container {
    max-width: 1000px;
    margin: auto;
}
"""
) as app:


    gr.Markdown("""
    <div class="hero">
        <h1>AI Literature Review Generator</h1>
        <p>Graph-Based Research Review System</p>
    </div>
    """)

    with gr.Column(elem_id="container"):

        with gr.Row():
            topic_input = gr.Textbox(
                label="Research Topic",
                placeholder="e.g., Transformer-based Sentiment Analysis",
                scale=4
            )
            generate_btn = gr.Button("Generate Review", scale=1)

        gr.Markdown("### Generated Outputs")

        with gr.Tabs():

            with gr.Tab("Cross-Paper Comparison"):
                comparison_output = gr.Textbox(
                    lines=15,
                    show_copy_button=True
                )

            with gr.Tab("Draft Review"):
                draft_output = gr.Textbox(
                    lines=15,
                    show_copy_button=True
                )

            with gr.Tab("Final Polished Review"):
                final_output = gr.Textbox(
                    lines=18,
                    show_copy_button=True
                )

        generate_btn.click(
            run_system,
            inputs=topic_input,
            outputs=[comparison_output, draft_output, final_output]
        )

app.launch()