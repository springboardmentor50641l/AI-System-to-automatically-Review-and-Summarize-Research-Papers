import datetime
from langgraph.graph import StateGraph
from graph.state import WorkflowState

from modules.analyzer import analyze_papers
from modules.draft_generator import generate_draft
from modules.reviewer import review_paper


# ---------------------------
# NODE DEFINITIONS
# ---------------------------

def analyze_node(state: WorkflowState) -> WorkflowState:
    state.analysis = analyze_papers(state.texts)
    return state


def draft_node(state: WorkflowState) -> WorkflowState:
    state.draft = generate_draft(state.analysis)
    return state


def review_node(state: WorkflowState) -> WorkflowState:
    state.reviewed = review_paper(state.draft)
    return state


# ---------------------------
# BUILD LANGGRAPH DAG
# ---------------------------

builder = StateGraph(WorkflowState)

builder.add_node("analyze", analyze_node)
builder.add_node("draft", draft_node)
builder.add_node("review", review_node)

builder.set_entry_point("analyze")

builder.add_edge("analyze", "draft")
builder.add_edge("draft", "review")

graph = builder.compile()


# ---------------------------
# WORKFLOW EXECUTION
# ---------------------------

def run_workflow(texts, topic, mode):
    """
    Executes real LangGraph DAG workflow.
    """

    try:
        # Initialize state
        state = WorkflowState(
            topic=topic,
            mode=mode,
            texts=texts
        )

        # Run graph (returns dict)
        final_state = graph.invoke(state.model_dump())

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        header = f"""
==================================================
AI Research Paper Review & Summarization System
==================================================

RESEARCH TOPIC : {final_state['topic']}
INPUT MODE     : {final_state['mode'].capitalize()}
GENERATED ON   : {timestamp}

--------------------------------------------------
"""

        reviewed_text = final_state.get("reviewed", "")

        final_output = (
            header
            + "\n"
            + reviewed_text.strip()
            + "\n\n--------------------------------------------------\n"
            + "End of Report\n"
            + "--------------------------------------------------"
        )

        return final_output

    except Exception as e:
        return f"Workflow execution error: {str(e)}"

