import gradio as gr
from main import run_pipeline

def run(topic, mode):
    return run_pipeline(topic, mode)

gr.Interface(
    fn=run,
    inputs=[
        gr.Textbox(label="Research Topic"),
        gr.Radio(
            ["automatic", "manual"],
            label="Paper Input Mode",
            value="automatic"
        )
    ],
    outputs=gr.Textbox(label="Final Reviewed Output"),
    title="AI Research Paper Review & Summarization System",
    description="Automatically reviews and compares research papers using Gemini API"
).launch()
