# import gradio as gr
# from main import run_pipeline

# def run(topic, mode):
#     return run_pipeline(topic, mode)

# gr.Interface(
#     fn=run,
#     inputs=[
#         gr.Textbox(label="Research Topic"),
#         gr.Radio(
#             ["automatic", "manual"],
#             label="Paper Input Mode",
#             value="automatic"
#         )
#     ],
#     outputs=gr.Textbox(label="Final Reviewed Output"),
#     title="AI Research Paper Review & Summarization System",
#     description="Automatically reviews and compares research papers using Gemini API"
# ).launch()
 # -------------------------------------------------------====================================----- #
import gradio as gr
from main import run_pipeline

def run(topic, mode, files):
    return run_pipeline(topic, mode, files)

with gr.Blocks() as demo:
    gr.Markdown("# AI Research Paper Review & Summarization System")

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

    submit_btn = gr.Button("Submit")

    submit_btn.click(
        fn=run,
        inputs=[topic, mode, file_upload],
        outputs=output
    )

demo.launch()
