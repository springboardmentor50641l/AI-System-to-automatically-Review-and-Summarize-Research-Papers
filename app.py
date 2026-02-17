import gradio as gr

# Soft Paris Chic Theme
custom_theme = gr.themes.Soft(
    primary_hue="pink",
    secondary_hue="rose",
)

custom_css = """
body {
    background-color: #ffffff !important;
    font-family: 'Helvetica Neue', sans-serif;
}

/* Textboxes (input + output) */
textarea, input {
    border-radius: 18px !important;
    border: 1px solid #f4c2d7 !important;
    background-color: #fff0f6 !important;  /* soft pink */
    color: #444 !important;
}

/* Specifically target output box */
[data-testid="textbox"] textarea {
    background-color: #ffe6f0 !important;
}

/* Buttons */
button {
    border-radius: 25px !important;
    background-color: #f8c8dc !important;
    color: #5a5a5a !important;
    font-weight: 400 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 8px rgba(248, 200, 220, 0.4) !important;
}

button:hover {
    background-color: #f4b6cc !important;
    box-shadow: 0 0 16px rgba(248, 200, 220, 0.7) !important;
    transform: scale(1.02);
}
"""


def hello(name):
    return f"Hello {name}, welcome to your soft AI empire ✨"

with gr.Blocks(theme=custom_theme, css=custom_css) as demo:
    gr.Markdown("## ✨ AI Research Review System")
    gr.Markdown("Minimal. Elegant. Intelligent.")

    name_input = gr.Textbox(label="Your Name")
    output = gr.Textbox(label="Output")

    btn = gr.Button("Test Interface")

    btn.click(hello, inputs=name_input, outputs=output)

demo.launch()

