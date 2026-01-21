import gradio as gr
from paper_search import automated_paper_search

def run(topic):
    dataset = automated_paper_search(topic)
    return f"Selected {len(dataset.papers)} papers successfully."

ui = gr.Interface(
    fn=run,
    inputs=gr.Textbox(label="Enter Research Topic"),
    outputs=gr.Textbox(label="Status"),
    title="Research Phase – Automated Paper Search"
)

if __name__ == "__main__":
    ui.launch()
