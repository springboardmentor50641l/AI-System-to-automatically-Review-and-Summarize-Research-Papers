import gradio as gr
import json

from final import generate_full_review
from qaulity.refinement import run_review_refinement
from qaulity.review import run_review_evaluation, load_final_review


# -------------------------
# HANDLERS
# -------------------------

def generate_handler(topic):
    try:
        result = generate_full_review(topic)
    except Exception as e:
        return f" Error: {str(e)}", None


    comparison_id = result["comparison_id"]
    version = result["version"]
    review_text = result["review_text"]
    evaluation = result["evaluation"]

    display = format_output(review_text, evaluation, version)

    state = {
        "comparison_id": comparison_id,
        "version": version
    }

    return display, state


def refine_handler(state):

    if state is None:
        return "📄 Please generate a review first.", state

    comparison_id = state["comparison_id"]
    version = state["version"]

    run_review_refinement(comparison_id, version)
    new_version = version + 1
    run_review_evaluation(comparison_id, new_version)

    review_text = load_final_review(comparison_id, new_version)

    eval_path = (
        f"text_extraction/output/review_comparison/"
        f"review_evaluation_{comparison_id}_v{new_version}.json"
    )

    with open(eval_path, "r", encoding="utf-8") as f:
        evaluation = json.load(f)

    display = format_output(review_text, evaluation, new_version)

    new_state = {
        "comparison_id": comparison_id,
        "version": new_version
    }

    return display, new_state


# -------------------------
# FORMAT OUTPUT
# -------------------------

def format_output(review_text, evaluation, version):

    return f"""
## 📄 Research Paper – Version {version}

---

{review_text}

---

📊 *Would you like to refine this version?*
"""

# CUSTOM PASTEL THEME


custom_css = """
body {
    background-color: #ffffff;
}

.gradio-container {
    font-family: 'Poppins', sans-serif;
}

h1 {
    text-align: center;
    color: #d63384;
    font-weight: 700;
}

.subtitle {
    text-align: center;
    color: #666;
    font-size: 18px;
    margin-bottom: 25px;
}

.creator {
    text-align: center;
    font-size: 14px;
    color: #c2185b;
    margin-bottom: 20px;
}

.pink-button {
    background-color: #f8c8dc !important;
    color: #6a1b4d !important;
    border-radius: 14px !important;
    box-shadow: 0 0 14px rgba(248, 200, 220, 0.8);
    transition: 0.3s ease-in-out;
}

.pink-button:hover {
    box-shadow: 0 0 25px rgba(248, 200, 220, 1);
    transform: scale(1.05);
}
.trend-button {
    background-color: #fdf0f5 !important;
    color: #6a1b4d !important;
    border-radius: 10px !important;
    margin-top: 6px;
}

"""

# UI


with gr.Blocks(css=custom_css) as demo:

    # HERO SECTION
    gr.Markdown("# 🧠 AI Research Studio")
    gr.Markdown("### ✨ Summarize • Review • Refine Research Papers")
    gr.Markdown("<div class='creator'>Created by Pari 💗</div>")

    gr.Markdown("---")

    # 🔬 PRIMARY ACTION (FIRST)
    gr.Markdown("## 🔬 Start Your Research")

    topic_input = gr.Textbox(
        placeholder="✨ Enter your research topic here...",
        lines=2,
        show_label=False
    )

    generate_btn = gr.Button(
        "✨ Generate Research Paper",
        elem_classes="pink-button"
    )

    output_box = gr.Markdown()
    state = gr.State()

    generate_btn.click(
        fn=generate_handler,
        inputs=topic_input,
        outputs=[output_box, state]
    )

    gr.Markdown("---")

    # TRENDING (SECONDARY)
    gr.Markdown("### 🎓 Or Explore Trending Topics")

    trending_topics = [
        "Explainable AI in Healthcare",
        "Large Language Models in Education",
        "AI for Climate Change Modeling",
        "Quantum Machine Learning",
        "Neural Architecture Search"
    ]

    for topic in trending_topics:
        btn = gr.Button(topic, elem_classes="trend-button")
        btn.click(lambda t=topic: t, outputs=topic_input)

    gr.Markdown("---")

    # REFINE SECTION
    refine_btn = gr.Button(
        "📈 Generate a Refined Version",
        elem_classes="pink-button"
    )

    refine_btn.click(
        fn=refine_handler,
        inputs=state,
        outputs=[output_box, state]
    )

demo.launch()




