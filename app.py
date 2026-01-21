import gradio as gr
from main import run_pipeline

def run(topic):
    return run_pipeline(topic)

gr.Interface(
    fn=run,
    inputs=gr.Textbox(label="Enter Research Topic"),
    outputs=gr.Textbox(label="Final Reviewed Paper", lines=25),
    title="AI Research Paper Reviewer (Gemini)",
    description="Automatically analyzes and summarizes research papers using Gemini API"
).launch()
