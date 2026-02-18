import os
import datetime
import gradio as gr

from main import run_pipeline
from config import OUTPUT_DIR
from utils.pdf_writer import save_text_as_pdf


# ================= GLOBAL STATE =================
last_saved_pdf = None


# ================= GENERATE =================
def generate(topic, mode, files):
    global last_saved_pdf
    last_saved_pdf = None  # reset previous file

    if not topic and mode == "automatic":
        return "", "⚠ Please enter a research topic.", None

    result = run_pipeline(topic, mode, files)

    if not result or result.strip() == "":
        return "", "❌ Generation failed.", None

    if "required" in result.lower() or "error" in result.lower():
        return result, "⚠ Generation returned warning.", None

    return result, "✅ Generation completed successfully.", None


# ================= SAVE =================
def save_output(text):
    global last_saved_pdf

    if not text or text.strip() == "":
        return "⚠ Nothing valid to save.", None

    error_keywords = ["At least two valid research papers are required for comparison.", "Please upload at least two PDF files for manual mode.", "Generation failed."]

    if any(keyword in text.lower() for keyword in error_keywords):
        return "⚠ Cannot save error message.", None

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    txt_path = os.path.join(OUTPUT_DIR, f"summary_{timestamp}.txt")
    pdf_path = os.path.join(OUTPUT_DIR, f"summary_{timestamp}.pdf")

    # Save TXT
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    # Save PDF
    save_text_as_pdf(text, pdf_path)

    last_saved_pdf = pdf_path

    return f" Saved Successfully:\n{pdf_path}", pdf_path


# ================= DOWNLOAD =================
def download_file():
    global last_saved_pdf
    return last_saved_pdf


# ================= CLEAR =================
def clear_all():
    global last_saved_pdf
    last_saved_pdf = None
    return "", None, "🧹 System cleared.", None


# ================= UI =================
with gr.Blocks(title="AI Research Review System") as demo:

    # -------- HEADER --------
    gr.Markdown(
        """
        # 📘 AI Research Paper Review & Summarization System  
        ### Automated Multi-Paper Comparative Analysis using Gemini AI
        """
    )

    with gr.Row():

        # -------- LEFT PANEL --------
        with gr.Column(scale=1):

            gr.Markdown("## 🔍 Input Configuration")

            topic = gr.Textbox(
                label="Research Topic",
                placeholder="Enter research topic (e.g., COVID-19 impact on LMICs)"
            )

            mode = gr.Radio(
                choices=["automatic", "manual"],
                label="Paper Input Mode",
                value="automatic"
            )

            file_upload = gr.File(
                label="Upload Research Papers (PDF - Minimum 2 for manual mode)",
                file_types=[".pdf"],
                file_count="multiple"
            )

            with gr.Row():
                submit_btn = gr.Button("🚀 Generate", variant="primary")
                save_btn = gr.Button("💾 Save")
                download_btn = gr.Button("⬇ Download")
                clear_btn = gr.Button("🧹 Clear")

            status = gr.Textbox(
                label="System Status",
                interactive=False
            )

        # -------- RIGHT PANEL --------
        with gr.Column(scale=2):

            gr.Markdown("## 📄 Generated Review Output")

            output = gr.Textbox(
                label="Final Reviewed Output",
                lines=30
            )

            download_output = gr.File(
                label="Download Generated PDF",
                interactive=False
            )

    # -------- BUTTON LOGIC --------
    submit_btn.click(
        fn=generate,
        inputs=[topic, mode, file_upload],
        outputs=[output, status, download_output]
    )

    save_btn.click(
        fn=save_output,
        inputs=output,
        outputs=[status, download_output]
    )

    download_btn.click(
        fn=download_file,
        outputs=download_output
    )

    clear_btn.click(
        fn=clear_all,
        outputs=[output, file_upload, status, download_output]
    )

    # -------- FOOTER --------
    gr.Markdown(
        """
        ---
        **Developed by Tanuj Kumar**  
        Infosys Springboard Internship Project  
        AI-based Academic Review Automation System
        """
    )


# Launch with theme (Gradio 6 compatible)
demo.launch(theme=gr.themes.Soft())
