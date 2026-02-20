#!/usr/bin/env python3
"""
Main Gradio Application with LangGraph Orchestration
Run: python src/app.py
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import TypedDict, List, Dict, Any, Optional, Generator
import gradio as gr
from loguru import logger
from langgraph.graph import StateGraph, END

# Add src to path to fix imports
sys.path.insert(0, str(Path(__file__).parent))

# Fix imports - import from config correctly
from config import (
    PAPERS_DIR, EXTRACTED_DIR, ANALYSIS_DIR, DRAFTS_DIR,
    MAX_PAPERS, LOGS_DIR
)
from utils import setup_logging, format_progress_message
from papersearch import PaperSearcher
from text_extraction import TextExtractor
from paper_analyzer import PaperAnalyzer
from draft_generator import DraftGenerator

# Setup logging
logger = setup_logging()

# ============================================================
# State Definition
# ============================================================

class PipelineState(TypedDict):
    """State object for LangGraph pipeline."""
    # Input
    topic: str
    
    # Milestone 1: Paper Search
    papers: List[Dict]
    search_success: bool
    search_message: str
    
    # Milestone 2: Extraction & Analysis
    extracted_paths: List[str]
    extraction_success: bool
    extraction_message: str
    
    analysis_paths: List[str]
    analysis_success: bool
    analysis_message: str
    
    # Milestone 3: Draft Generation
    draft: Optional[str]
    draft_path: Optional[str]
    draft_success: bool
    draft_message: str
    
    # Pipeline status
    error: Optional[str]
    progress: List[str]
    start_time: float
    stage_times: Dict[str, float]

def create_initial_state(topic: str) -> PipelineState:
    """Create initial pipeline state."""
    return {
        "topic": topic,
        "papers": [],
        "search_success": False,
        "search_message": "",
        "extracted_paths": [],
        "extraction_success": False,
        "extraction_message": "",
        "analysis_paths": [],
        "analysis_success": False,
        "analysis_message": "",
        "draft": None,
        "draft_path": None,
        "draft_success": False,
        "draft_message": "",
        "error": None,
        "progress": [],
        "start_time": time.time(),
        "stage_times": {}
    }

# ============================================================
# Pipeline Nodes
# ============================================================

def search_node(state: PipelineState) -> PipelineState:
    """Node 1: Search and download papers."""
    stage_start = time.time()
    
    try:
        state["progress"].append(format_progress_message(
            "search", f"Searching for papers on: '{state['topic']}'"
        ))
        
        searcher = PaperSearcher()
        result = searcher.process_topic(state["topic"])
        
        state["papers"] = result["papers"]
        state["search_success"] = result["success"]
        state["search_message"] = result["message"]
        
        if not result["success"]:
            state["error"] = result["message"]
            state["progress"].append(format_progress_message(
                "error", f"Search failed: {result['message']}"
            ))
        else:
            state["progress"].append(format_progress_message(
                "complete", f"Found {len(result['papers'])} papers with PDFs"
            ))
            
            for i, paper in enumerate(result["papers"], 1):
                state["progress"].append(f"   {i}. {paper['title'][:80]}...")
        
    except Exception as e:
        logger.error(f"Search node error: {e}")
        state["error"] = str(e)
        state["progress"].append(format_progress_message(
            "error", f"Search failed: {e}"
        ))
    
    state["stage_times"]["search"] = time.time() - stage_start
    return state

def extract_node(state: PipelineState) -> PipelineState:
    """Node 2: Extract text from PDFs."""
    stage_start = time.time()
    
    if state.get("error"):
        return state
    
    try:
        state["progress"].append(format_progress_message(
            "extract", "Extracting text from PDFs..."
        ))
        
        extractor = TextExtractor()
        saved_files = extractor.process_all_pdfs(PAPERS_DIR)
        
        state["extracted_paths"] = saved_files
        state["extraction_success"] = len(saved_files) > 0
        state["extraction_message"] = f"Extracted {len(saved_files)} papers"
        
        if saved_files:
            state["progress"].append(format_progress_message(
                "complete", f"Successfully extracted text from {len(saved_files)} papers"
            ))
            
            for path in saved_files[:3]:
                state["progress"].append(f"   📄 {Path(path).name}")
        else:
            state["error"] = "No text extracted from any PDF"
            state["progress"].append(format_progress_message(
                "error", "Failed to extract text from any PDF"
            ))
        
    except Exception as e:
        logger.error(f"Extraction node error: {e}")
        state["error"] = str(e)
        state["progress"].append(format_progress_message(
            "error", f"Extraction failed: {e}"
        ))
    
    state["stage_times"]["extract"] = time.time() - stage_start
    return state

def analyze_node(state: PipelineState) -> PipelineState:
    """Node 3: Analyze extracted papers."""
    stage_start = time.time()
    
    if state.get("error"):
        return state
    
    try:
        state["progress"].append(format_progress_message(
            "analyze", "Analyzing papers with Gemini AI..."
        ))
        
        analyzer = PaperAnalyzer()
        analysis_paths = analyzer.process_all_papers(EXTRACTED_DIR)
        
        state["analysis_paths"] = analysis_paths
        state["analysis_success"] = len(analysis_paths) > 0
        state["analysis_message"] = f"Analyzed {len(analysis_paths)} papers"
        
        if analysis_paths:
            state["progress"].append(format_progress_message(
                "complete", f"Successfully analyzed {len(analysis_paths)} papers"
            ))
            
            for path in analysis_paths[:3]:
                state["progress"].append(f"   🔬 {Path(path).name}")
        else:
            state["error"] = "No papers successfully analyzed"
            state["progress"].append(format_progress_message(
                "error", "Failed to analyze any papers"
            ))
        
    except Exception as e:
        logger.error(f"Analysis node error: {e}")
        state["error"] = str(e)
        state["progress"].append(format_progress_message(
            "error", f"Analysis failed: {e}"
        ))
    
    state["stage_times"]["analyze"] = time.time() - stage_start
    return state

def draft_node(state: PipelineState) -> PipelineState:
    """Node 4: Generate final draft."""
    stage_start = time.time()
    
    if state.get("error"):
        return state
    
    try:
        state["progress"].append(format_progress_message(
            "draft", "Generating research review draft..."
        ))
        
        generator = DraftGenerator()
        result = generator.generate_review(state["topic"])
        
        state["draft_success"] = result["success"]
        state["draft_message"] = result["message"]
        
        if result["success"]:
            state["draft"] = result["draft"]
            state["draft_path"] = result["draft_path"]
            
            state["progress"].append(format_progress_message(
                "complete", f"Draft generated successfully: {result['draft_path']}"
            ))
            
            preview = result["draft"][:200] + "..." if len(result["draft"]) > 200 else result["draft"]
            state["progress"].append(f"   📝 Preview: {preview}")
        else:
            state["error"] = result["message"]
            state["progress"].append(format_progress_message(
                "error", f"Draft generation failed: {result['message']}"
            ))
        
    except Exception as e:
        logger.error(f"Draft node error: {e}")
        state["error"] = str(e)
        state["progress"].append(format_progress_message(
            "error", f"Draft generation failed: {e}"
        ))
    
    state["stage_times"]["draft"] = time.time() - stage_start
    return state

def finalize_node(state: PipelineState) -> PipelineState:
    """Final node: Calculate total time and prepare output."""
    total_time = time.time() - state["start_time"]
    
    state["progress"].append("\n" + "="*50)
    state["progress"].append("📊 PIPELINE SUMMARY")
    state["progress"].append("="*50)
    
    if state.get("error"):
        state["progress"].append(f"❌ Status: Failed")
        state["progress"].append(f"⚠️ Error: {state['error']}")
    else:
        state["progress"].append(f"✅ Status: Completed Successfully")
        state["progress"].append(f"📚 Papers processed: {len(state.get('papers', []))}")
        state["progress"].append(f"⏱️ Total time: {total_time:.1f} seconds")
        
        state["progress"].append("\n📈 Stage Times:")
        for stage, duration in state["stage_times"].items():
            state["progress"].append(f"   • {stage.capitalize()}: {duration:.1f}s")
    
    return state

# ============================================================
# Build LangGraph Pipeline
# ============================================================

def build_pipeline() -> StateGraph:
    """Construct the LangGraph pipeline."""
    
    graph = StateGraph(PipelineState)
    
    graph.add_node("search", search_node)
    graph.add_node("extract", extract_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("draft", draft_node)
    graph.add_node("finalize", finalize_node)
    
    graph.set_entry_point("search")
    
    graph.add_edge("search", "extract")
    graph.add_edge("extract", "analyze")
    graph.add_edge("analyze", "draft")
    graph.add_edge("draft", "finalize")
    graph.add_edge("finalize", END)
    
    return graph.compile()

# ============================================================
# Gradio Interface
# ============================================================

def run_pipeline(topic: str) -> Generator:
    """Run the complete pipeline with progress updates."""
    if not topic or not topic.strip():
        yield "❌ Please enter a valid research topic.", ""
        return
    
    initial_state = create_initial_state(topic.strip())
    pipeline = build_pipeline()
    
    try:
        final_state = pipeline.invoke(initial_state)
        progress_text = "\n".join(final_state["progress"])
        
        draft_text = ""
        if final_state.get("draft"):
            generator = DraftGenerator()
            draft_text = generator.format_draft_for_display(final_state["draft"])
        
        yield progress_text, draft_text
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        error_msg = format_progress_message("error", f"Pipeline failed: {e}")
        yield error_msg, ""

def create_ui() -> gr.Blocks:
    """Create the Gradio UI."""
    
    with gr.Blocks(
        title="Automated Research Review System",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="indigo",
            neutral_hue="gray"
        ),
    ) as demo:
        
        gr.Markdown("""
        # 📚 Automated Research Review System
        
        Enter a research topic below to automatically:
        1. 🔍 Search and download relevant papers
        2. 📄 Extract and normalize text from PDFs
        3. 🔬 Analyze papers using Gemini AI
        4. ✍️ Generate a structured research review draft
        """)
        
        with gr.Row():
            with gr.Column(scale=4):
                topic_input = gr.Textbox(
                    label="🔬 Research Topic",
                    placeholder="e.g., machine learning transformers",
                    lines=2
                )
            with gr.Column(scale=1):
                run_btn = gr.Button("🚀 Run Pipeline", variant="primary", size="lg")
        
        with gr.Row():
            with gr.Column(scale=1):
                progress_output = gr.Textbox(
                    label="📊 Pipeline Progress",
                    lines=20,
                    max_lines=30,
                    interactive=False
                )
            with gr.Column(scale=1):
                draft_output = gr.Textbox(
                    label="📝 Generated Draft",
                    lines=20,
                    max_lines=30,
                    interactive=False
                )
        
        run_btn.click(
            fn=run_pipeline,
            inputs=topic_input,
            outputs=[progress_output, draft_output],
            queue=True
        )
        
        gr.Examples(
            examples=[
                ["machine learning transformers"],
                ["graph neural networks"],
                ["deep learning in healthcare"],
            ],
            inputs=topic_input,
        )
    
    return demo

# ============================================================
# Main Entry Point
# ============================================================

def main():
    """Main entry point for the application."""
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     Automated Research Review System with LangGraph     ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    demo = create_ui()
    
    print("\n🚀 Starting Gradio server...")
    print("📡 Local URL: http://127.0.0.1:7860")
    print("\nPress Ctrl+C to stop the server\n")
    
    demo.queue(max_size=10)
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True
    )

if __name__ == "__main__":
    main()