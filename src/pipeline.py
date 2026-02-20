"""
pipeline.py
────────────
Full LangGraph pipeline for the AI Research Review System.

Graph: __start__
  → process_input → planner → search_articles → article_decisions
  → download_articles → extract_text → normalize_text → semantic_section
  → validate_sections → store_sections → paper_analyzer → cross_compare
  → [write_abstract, write_introduction, write_methods, write_results,
     write_conclusion, write_references]  (parallel fan-out)
  → aggregate_paper → critique_paper
  → conditional: revise_paper (loop) or final_draft
  → __end__

Public API:
    build_pipeline()   → compiled graph
    run_pipeline(topic, progress_callback) → PaperState
    run_search_only(topic)    → PaperState up to download
    run_generate_only(state)  → PaperState from analysis onward
    run_revise_only(state)    → PaperState revision cycle only
"""

from __future__ import annotations

import os
from typing import Callable

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from .state import PaperState                   # ✅
from .paper_search import (                     # ✅ correct name + dot
    process_input_node,
    planner_node,
    search_articles_node,
    article_decisions_node,
    download_articles_node,
)
from .text_extraction import (                  # ✅
    extract_text_node,
    normalize_text_node,
    semantic_section_node,
    validate_sections_node,
    store_sections_node,
)
from .paper_analyzer import (                   # ✅
    paper_analyzer_node,
    cross_compare_node,
)
from .draft_generator import (                  # ✅
    write_abstract_node,
    write_introduction_node,
    write_methods_node,
    write_results_node,
    write_conclusion_node,
    write_references_node,
    aggregate_paper_node,
    critique_paper_node,
    revise_node,
    revise_paper_node,
    final_draft_node,
)
from .logger import get_logger  

load_dotenv()
logger = get_logger(__name__)


# ── Graph construction ────────────────────────────────────────────────────────

def build_pipeline() -> object:
    """Build and compile the full LangGraph review pipeline."""
    graph = StateGraph(PaperState)

    # ── Milestone 1: Search & Download ───────────────────────────────────────
    graph.add_node("process_input", process_input_node)
    graph.add_node("planner", planner_node)
    graph.add_node("search_articles", search_articles_node)
    graph.add_node("article_decisions", article_decisions_node)
    graph.add_node("download_articles", download_articles_node)

    # ── Milestone 2: Extraction & Sectioning ─────────────────────────────────
    graph.add_node("extract_text", extract_text_node)
    graph.add_node("normalize_text", normalize_text_node)
    graph.add_node("semantic_section", semantic_section_node)
    graph.add_node("validate_sections", validate_sections_node)
    graph.add_node("store_sections", store_sections_node)

    # ── Milestone 3: Analysis ─────────────────────────────────────────────────
    graph.add_node("paper_analyzer", paper_analyzer_node)
    graph.add_node("cross_compare", cross_compare_node)

    # ── Milestone 3: Draft writing ────────────────────────────────────────────
    graph.add_node("write_abstract", write_abstract_node)
    graph.add_node("write_introduction", write_introduction_node)
    graph.add_node("write_methods", write_methods_node)
    graph.add_node("write_results", write_results_node)
    graph.add_node("write_conclusion", write_conclusion_node)
    graph.add_node("write_references", write_references_node)

    # ── Milestone 3/4: Assembly ───────────────────────────────────────────────
    graph.add_node("aggregate_paper", aggregate_paper_node)

    # ── Milestone 4: Review & Finalize ───────────────────────────────────────
    graph.add_node("critique_paper", critique_paper_node)
    graph.add_node("revise_paper", revise_paper_node)
    graph.add_node("final_draft", final_draft_node)

    # ── Entry point ───────────────────────────────────────────────────────────
    graph.set_entry_point("process_input")

    # ── Milestone 1 edges ─────────────────────────────────────────────────────
    graph.add_edge("process_input", "planner")
    graph.add_edge("planner", "search_articles")
    graph.add_edge("search_articles", "article_decisions")
    graph.add_edge("article_decisions", "download_articles")

    # ── Milestone 2 edges ─────────────────────────────────────────────────────
    graph.add_edge("download_articles", "extract_text")
    graph.add_edge("extract_text", "normalize_text")
    graph.add_edge("normalize_text", "semantic_section")
    graph.add_edge("semantic_section", "validate_sections")
    graph.add_edge("validate_sections", "store_sections")

    # ── Milestone 3 analysis edges ────────────────────────────────────────────
    graph.add_edge("store_sections", "paper_analyzer")
    graph.add_edge("paper_analyzer", "cross_compare")

    # ── Parallel section writing ──────────────────────────────────────────────
    # LangGraph fan-out: cross_compare → multiple write nodes (sequential chain)
    # LangGraph OSS does not natively support true parallelism, so we chain them.
    graph.add_edge("cross_compare", "write_abstract")
    graph.add_edge("write_abstract", "write_introduction")
    graph.add_edge("write_introduction", "write_methods")
    graph.add_edge("write_methods", "write_results")
    graph.add_edge("write_results", "write_conclusion")
    graph.add_edge("write_conclusion", "write_references")
    graph.add_edge("write_references", "aggregate_paper")

    # ── Milestone 4 edges ─────────────────────────────────────────────────────
    graph.add_edge("aggregate_paper", "critique_paper")
    graph.add_conditional_edges(
        "critique_paper",
        revise_node,
        {
            "revise_paper": "revise_paper",
            "final_draft": "final_draft",
        },
    )
    # After revision, re-critique (loop with max 2 iterations enforced in revise_node)
    graph.add_edge("revise_paper", "critique_paper")
    graph.add_edge("final_draft", END)

    compiled = graph.compile()
    logger.info("LangGraph pipeline compiled successfully.")
    return compiled


# ── Run helpers ───────────────────────────────────────────────────────────────

def run_pipeline(
    topic: str,
    progress_callback: Callable[[str, list[str]], None] | None = None,
) -> PaperState:
    """
    Run the complete pipeline for a given topic.

    Args:
        topic: Research topic string.
        progress_callback: Optional function called after each node with
                           (current_step, step_log) for live UI updates.

    Returns:
        Final PaperState after the pipeline completes.
    """
    pipeline = build_pipeline()
    initial_state: PaperState = {
        "topic": topic,
        "step_log": [],
        "errors": [],
        "revision_count": 0,
    }

    final_state = initial_state
    try:
        for event in pipeline.stream(initial_state, stream_mode="updates"):
            for node_name, node_output in event.items():
                if isinstance(node_output, dict):
                    final_state = {**final_state, **node_output}
                    step = final_state.get("current_step", node_name)
                    log = final_state.get("step_log", [])
                    logger.info("Node completed: %s", node_name)
                    if progress_callback:
                        progress_callback(step, log)
    except Exception as exc:
        logger.error("Pipeline error: %s", exc)
        final_state = {
            **final_state,
            "errors": final_state.get("errors", []) + [str(exc)],
        }

    return final_state


def run_search_only(topic: str) -> PaperState:
    """Run only the search and download phase (Milestone 1)."""
    from .paper_search import (
        process_input_node,
        planner_node,
        search_articles_node,
        article_decisions_node,
        download_articles_node,
    )

    state: PaperState = {
        "topic": topic,
        "step_log": [],
        "errors": [],
        "revision_count": 0,
    }
    state = process_input_node(state)
    state = planner_node(state)
    state = search_articles_node(state)
    state = article_decisions_node(state)
    state = download_articles_node(state)
    return state


def run_generate_only(state: PaperState) -> PaperState:
    """
    Run from extraction through final draft, given a state that already
    has downloaded_pdfs and selected_papers populated.
    """
    from .text_extraction import (
        extract_text_node, normalize_text_node, semantic_section_node,
        validate_sections_node, store_sections_node,
    )
    from .paper_analyzer import paper_analyzer_node, cross_compare_node
    from .draft_generator import (
        write_abstract_node, write_introduction_node, write_methods_node,
        write_results_node, write_conclusion_node, write_references_node,
        aggregate_paper_node, critique_paper_node, revise_node,
        revise_paper_node, final_draft_node,
    )

    for fn in [
        extract_text_node, normalize_text_node, semantic_section_node,
        validate_sections_node, store_sections_node,
        paper_analyzer_node, cross_compare_node,
        write_abstract_node, write_introduction_node, write_methods_node,
        write_results_node, write_conclusion_node, write_references_node,
        aggregate_paper_node,
    ]:
        state = fn(state)

    state = critique_paper_node(state)
    decision = revise_node(state)
    if decision == "revise_paper":
        state = revise_paper_node(state)
        state = critique_paper_node(state)
    state = final_draft_node(state)
    return state


def run_revise_only(state: PaperState) -> PaperState:
    """
    Run just the critique → revise → final_draft cycle.
    Expects aggregated_draft to already be set.
    """
    state = {"revision_count": 0, **state}
    state = critique_paper_node(state)
    state = revise_paper_node(state)
    state = critique_paper_node(state)
    state = final_draft_node(state)
    return state