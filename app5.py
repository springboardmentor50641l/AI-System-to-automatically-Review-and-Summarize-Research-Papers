import gradio as gr
from pathlib import Path
from final import generate_full_review
from user_input import generate_review_from_pdf
from qaulity.refinement import run_review_refinement


# ===============================
# Clean Academic Theme
# ===============================

custom_css = """
:root {
    --color-primary: #F49CBB !important;
    --color-accent: #F49CBB !important;
    --background-fill-primary: #FFFFFF !important;
    --background-fill-secondary: #FFFFFF !important;
    --block-background-fill: #FFFFFF !important;
}

/* ========================= */
/* GLOBAL RESET              */
/* ========================= */

* {
    border-radius: 0px !important;
    box-shadow: none !important;
}

body,
.gradio-container,
.gr-block,
.gr-box,
.gr-panel,
.gr-group,
.gr-form,
div {
    background: #FFFFFF !important;
    background-color: #FFFFFF !important;
}

/* Remove all focus glow globally */
*:focus,
*:focus-visible {
    outline: none !important;
    box-shadow: none !important;
}

/* ========================= */
/* TYPOGRAPHY                */
/* ========================= */

.gradio-container {
    font-family: 'Inter', sans-serif;
    color: #111111 !important;
}

h1 {
    color: #F49CBB !important;
    font-weight: 700;
    border-bottom: 2px solid #F49CBB !important;
    padding-bottom: 8px;
}

.gr-markdown p {
    color: #333333 !important;
}

label {
    color: #111111 !important;
    font-weight: 600 !important;
}

/* ========================= */
/* TEXTBOXES                 */
/* ========================= */

div[data-testid="textbox"],
.gr-textbox,
.gr-textbox > div,
textarea,
input {
    background: #FFFFFF !important;
}

div[data-testid="textbox"],
.gr-textbox {
    border: 2px solid #F49CBB !important;
}

/* Internal input cleanup */
textarea,
input {
    border: none !important;
    padding: 14px !important;
    color: #111111 !important;
}

/* Focus state = darker pink */
div[data-testid="textbox"]:focus-within,
.gr-textbox:focus-within {
    border: 2px solid #E678A5 !important;
}

/* ========================= */
/* FILE UPLOAD               */
/* ========================= */

div[data-testid="file-upload"],
.gr-file,
.gr-file > div {
    border: 2px solid #F49CBB !important;
    background: #FFFFFF !important;
}

/* Remove drag hover color */
.gr-file.dragging {
    border: 2px solid #E678A5 !important;
    background: #FFFFFF !important;
}

/* ========================= */
/* BUTTONS                   */
/* ========================= */

button {
    background: #FFFFFF !important;
    color: #F49CBB !important;
    border: 2px solid #F49CBB !important;
    padding: 12px 26px !important;
    font-weight: 600;
    transition: all 0.2s ease;
}

button:hover {
    background: #F49CBB !important;
    color: #FFFFFF !important;
}

button:active {
    background: #E678A5 !important;
    border-color: #E678A5 !important;
}

/* Remove Gradio accent layers */
button.primary,
button.secondary {
    background: #FFFFFF !important;
}

/* ========================= */
/* TABS                      */
/* ========================= */

.tab-nav button {
    background: transparent !important;
    border: none !important;
    color: #111111 !important;
}

.tab-nav button.selected {
    border-bottom: 3px solid #F49CBB !important;
    color: #F49CBB !important;
}

/* Remove tab hover accent */
.tab-nav button:hover {
    background: #FFFFFF !important;
}

/* ========================= */
/* SCROLLBAR (Clean)         */
/* ========================= */

::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: #F49CBB;
}

::-webkit-scrollbar-track {
    background: #FFFFFF;
}

/* ========================= */
/* FOOTER                    */
/* ========================= */

footer {
    text-align: center;
    font-size: 12px;
    color: #999999;
    margin-top: 40px;
}
"""


# ===============================
# Backend Logic (UNCHANGED)
# ===============================

def handle_pdf_upload(file):
    try:
        if file is None:
            return " Please upload a PDF file.", None, None, None, None

        result = generate_review_from_pdf(file.name)
        comparison_id = result.get("comparison_id")
        version = int(result.get("version", 1))
        review_text = result.get("review_text", "")

        file_path = Path(
            f"text_extraction/output/review_comparison/"
            f"final_review_{comparison_id}_v{version}.txt"
        )

        if not file_path.exists():
            return "Review generated but file not found.", None, comparison_id, version, None

        return review_text, None, comparison_id, version, str(file_path)

    except Exception as e:
        return f" Error generating review: {str(e)}", None, None, None, None


def handle_topic(topic):
    try:
        if not topic or topic.strip() == "":
            return " Please enter a topic.", None, None, None, None

        result = generate_full_review(topic)
        comparison_id = result.get("comparison_id")
        version = int(result.get("version", 1))
        review_text = result.get("review_text", "")

        file_path = Path(
            f"text_extraction/output/review_comparison/"
            f"final_review_{comparison_id}_v{version}.txt"
        )

        if not file_path.exists():
            return "⚠ Review generated but file not found.", None, comparison_id, version, None

        return review_text, None, comparison_id, version, str(file_path)

    except Exception as e:
        return f" Error generating review: {str(e)}", None, None, None, None


def handle_refinement(comparison_id, version, current_original):
    try:
        if comparison_id is None or version is None:
            return current_original, " Generate a review first.", version, None

        version = int(version)
        new_file_path = run_review_refinement(comparison_id, version)

        if not new_file_path:
            return current_original, " Refinement failed.", version, None

        new_file_path = Path(new_file_path)

        if not new_file_path.exists():
            return current_original, " Refined file not found.", version, None

        refined_text = new_file_path.read_text(encoding="utf-8")
        new_version = version + 1

        #  Return original unchanged
        return current_original, refined_text, new_version, str(new_file_path)

    except Exception as e:
        return current_original, f" Error during refinement: {str(e)}", version, None


# ===============================
# UI
# ===============================

with gr.Blocks(
    css=custom_css,
    title="AI Literature Review Generator",
    theme=gr.themes.Base()
) as demo:

    # Suggested Topics (BLACK — correct hierarchy)
    gr.Markdown(
        "<div style='font-size:11px; color:#111111;'>"
        "Suggested Topics: Vision Transformers | Self-Supervised Learning | DINO vs MAE | NLP in Healthcare | Diffusion Models"
        "</div>"
    )

    gr.Markdown("# AI Literature Review Generator")

    gr.Markdown(
        "Generate structured AI-powered literature reviews from research papers or custom topics. "
        "Upload a PDF or enter a topic to create a version-controlled academic review."
    )

    comparison_id_state = gr.State()
    version_state = gr.State()

    with gr.Tab("Upload Research Paper"):
        pdf_input = gr.File(file_types=[".pdf"])
        generate_pdf_btn = gr.Button("Generate Review")

    with gr.Tab("Enter Topic"):
        topic_input = gr.Textbox(label="Enter Topic e.g Artificial Intelligence")
        generate_topic_btn = gr.Button("Generate Review")

    with gr.Row():
        original_output = gr.Textbox(label="Original Review", lines=20)
        refined_output = gr.Textbox(label="Refined Review", lines=20)

    with gr.Row():
        download_original = gr.File(label="Download Original Review")
        download_refined = gr.File(label="Download Refined Review")

    refine_btn = gr.Button("Refine Review")

    generate_pdf_btn.click(
        fn=handle_pdf_upload,
        inputs=pdf_input,
        outputs=[
            original_output,
            refined_output,
            comparison_id_state,
            version_state,
            download_original
        ]
    )

    generate_topic_btn.click(
        fn=handle_topic,
        inputs=topic_input,
        outputs=[
            original_output,
            refined_output,
            comparison_id_state,
            version_state,
            download_original
        ]
    )

    refine_btn.click(
    fn=handle_refinement,
    inputs=[comparison_id_state, version_state, original_output],
        outputs=[
            original_output,
            refined_output,
            version_state,
            download_refined
        ]
    )


demo.launch()