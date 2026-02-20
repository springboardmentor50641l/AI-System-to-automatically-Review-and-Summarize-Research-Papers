import streamlit as st
import json
import time
import re

st.set_page_config(page_title="AI Research Writing System", layout="wide")

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def slugify(text):
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


# -------------------------------------------------
# Session State Init
# -------------------------------------------------
if "active_topic" not in st.session_state:
    st.session_state.active_topic = ""

if "draft" not in st.session_state:
    st.session_state.draft = {
        "abstract": "",
        "methods_comparison": "",
        "results_synthesis": "",
        "discussion": "",
        "conclusion": "",
        "references": ""
    }

if "scores" not in st.session_state:
    st.session_state.scores = {
        "Abstract": "-",
        "Methods": "-",
        "Results": "-",
        "Discussion": "-"
    }


# -------------------------------------------------
# Header
# -------------------------------------------------
st.title("🧠 AI-Powered Literature Review Dashboard")
st.markdown("Professional AI-assisted Research Writing System")


# -------------------------------------------------
# Pipeline Control Panel
# -------------------------------------------------
st.markdown("## 🚀 Research Pipeline")

col1, col2, col3 = st.columns([4, 2, 2])

with col1:
    topic_input = st.text_input("Research Topic")

with col2:
    paper_limit = st.slider("Paper Limit", 3, 20, 5)

with col3:
    run_button = st.button("Run Pipeline")

if run_button and topic_input:
    st.session_state.active_topic = slugify(topic_input)

    with st.spinner("Running pipeline..."):
        time.sleep(2)

        # Demo Draft Content
        st.session_state.draft = {
            "abstract": f"This literature review examines recent developments in {topic_input}.",
            "methods_comparison": "Studies employed experimental, simulation, and comparative methodologies.",
            "results_synthesis": "Most works report performance improvements, though evaluation metrics vary.",
            "discussion": "Despite promising results, scalability and dataset bias remain critical limitations.",
            "conclusion": "Future research should emphasize robustness and real-world validation.",
            "references": "Author A (2022); Author B (2023)"
        }

    st.success("Pipeline completed successfully.")


# -------------------------------------------------
# Quality Dashboard
# -------------------------------------------------
st.markdown("## 📊 Section Quality Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Abstract", st.session_state.scores["Abstract"])
c2.metric("Methods", st.session_state.scores["Methods"])
c3.metric("Results", st.session_state.scores["Results"])
c4.metric("Discussion", st.session_state.scores["Discussion"])


# -------------------------------------------------
# Section Workspace
# -------------------------------------------------
st.markdown("## 📝 Review Workspace")

tabs = st.tabs([
    "Abstract",
    "Methods",
    "Results",
    "Discussion",
    "Conclusion",
    "References"
])

section_map = {
    "Abstract": "abstract",
    "Methods": "methods_comparison",
    "Results": "results_synthesis",
    "Discussion": "discussion",
    "Conclusion": "conclusion",
    "References": "references"
}

for tab_name, tab in zip(section_map.keys(), tabs):
    with tab:
        key = section_map[tab_name]

        edited_text = st.text_area(
            tab_name,
            value=st.session_state.draft.get(key, ""),
            height=250,
            key=f"edit_{key}"
        )

        st.session_state.draft[key] = edited_text

        colA, colB = st.columns(2)

        with colA:
            if st.button(f"🔍 Critique {tab_name}", key=f"crit_{key}"):
                st.session_state.scores[tab_name] = "7.8 / 10"
                st.info("Strong structure. Add deeper analytical comparison.")

        with colB:
            if st.button(f"✏ Improve {tab_name}", key=f"rev_{key}"):
                improved = edited_text + "\n\n(Refined for academic clarity and coherence.)"
                st.session_state.draft[key] = improved
                st.success("Section improved.")


# -------------------------------------------------
# Export
# -------------------------------------------------
st.markdown("## 📤 Export")

json_export = json.dumps(st.session_state.draft, indent=2)

st.download_button(
    "Download JSON",
    data=json_export,
    file_name="literature_review.json",
    mime="application/json"
)

text_export = "\n\n".join(
    [f"{k.upper()}\n{v}" for k, v in st.session_state.draft.items()]
)

st.download_button(
    "Download TXT",
    data=text_export,
    file_name="literature_review.txt",
    mime="text/plain"
)
