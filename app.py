
import os
import datetime
import gradio as gr

from main import run_pipeline
from config import OUTPUT_DIR
from utils.pdf_writer import save_text_as_pdf

# Global variable to store last saved PDF path
last_saved_pdf = None


# ================= GENERATE =================
def generate(topic, mode, files):
    result = run_pipeline(topic, mode, files)

    if not result or result.strip() == "":
        return "", "Generation failed.", None

    return result, "Generation completed successfully.", None


# ================= SAVE =================
def save_output(text):
    global last_saved_pdf

    if not text or text.strip() == "":
        return "Nothing valid to save.", None

    error_keywords = ["required", "error", "failed", "please upload"]

    if any(keyword in text.lower() for keyword in error_keywords):
        return "Cannot save error message.", None

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

    return f"Saved successfully:\n{pdf_path}", pdf_path


# ================= DOWNLOAD =================
def download_file():
    global last_saved_pdf

    if not last_saved_pdf:
        return None

    return last_saved_pdf


# ================= CLEAR =================
def clear_all():
    global last_saved_pdf
    last_saved_pdf = None
    return "", None, "System cleared.", None


# ================= UI =================
with gr.Blocks() as demo:

    gr.Markdown("# 📘 AI Research Paper Review & Summarization System")

    topic = gr.Textbox(label="Research Topic")

    mode = gr.Radio(
        choices=["automatic", "manual"],
        label="Paper Input Mode",
        value="automatic"
    )

    file_upload = gr.File(
        label="Upload Research Papers (PDF)",
        file_types=[".pdf"],
        file_count="multiple"
    )

    output = gr.Textbox(
        label="Final Reviewed Output",
        lines=25
    )

    status = gr.Textbox(
        label="System Status",
        interactive=False
    )

    download_output = gr.File(
        label="Download Generated PDF",
        interactive=False
    )

    with gr.Row():
        submit_btn = gr.Button("Generate")
        save_btn = gr.Button("Save")
        download_btn = gr.Button("Download")
        clear_btn = gr.Button("Clear")

    # Generate
    submit_btn.click(
        fn=generate,
        inputs=[topic, mode, file_upload],
        outputs=[output, status, download_output]
    )

    # Save
    save_btn.click(
        fn=save_output,
        inputs=output,
        outputs=[status, download_output]
    )

    # Download
    download_btn.click(
        fn=download_file,
        outputs=download_output
    )

    # Clear
    clear_btn.click(
        fn=clear_all,
        outputs=[output, file_upload, status, download_output]
    )

demo.launch()


