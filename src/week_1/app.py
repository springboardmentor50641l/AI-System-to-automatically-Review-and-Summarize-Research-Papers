import gradio as gr
from paper_search import automated_paper_search

def run(topic):
    try:
        dataset = automated_paper_search(topic, max_papers=3)

        # collect pdf paths
        file_paths = [paper.pdf_path for paper in dataset.papers]

        status = f"Successfully downloaded {len(dataset.papers)} papers."
        return status, file_paths

    except Exception as e:
        return f"Error: {str(e)}", []

ui = gr.Interface(
    fn=run,
    inputs=gr.Textbox(label="Enter Research Topic"),
    outputs=[
        gr.Textbox(label="Status"),
        gr.Files(label="Downloaded Papers")
    ],
    title="Research Phase – Automated Paper Search"
)

if __name__ == "__main__":
    ui.launch()
