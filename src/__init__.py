#!/usr/bin/env python3
"""
Automated Research Review System
A complete pipeline for searching, analyzing, and summarizing research papers.

This package provides modular components for:
- Paper search and download (Semantic Scholar API)
- Text extraction from PDFs (PyMuPDF)
- Semantic analysis using Gemini AI
- Draft generation with LangGraph orchestration
- Gradio web interface

Author: Infosys Springboard Intern
Version: 1.0.0
"""

import sys
import os
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Package metadata
__version__ = "1.0.0"
__author__ = "Infosys Springboard Intern"
__email__ = "intern@infosys.com"
__license__ = "MIT"
__description__ = "Automated Research Review System with LangGraph and Gemini AI"

# Export main components for easy import
from .config import (
    BASE_DIR,
    DATA_DIR,
    PAPERS_DIR,
    EXTRACTED_DIR,
    ANALYSIS_DIR,
    DRAFTS_DIR,
    LOGS_DIR,
    GEMINI_API_KEY,
    MAX_PAPERS
)

from .utils import (
    setup_logging,
    count_tokens,
    chunk_text,
    safe_json_loads,
    sanitize_filename,
    format_progress_message
)

from .papersearch import PaperSearcher
from .text_extraction import TextExtractor
from .paper_analyzer import PaperAnalyzer
from .draft_generator import DraftGenerator

# Optional: Create convenience functions
def create_directories():
    """Create all necessary directories if they don't exist."""
    directories = [
        DATA_DIR,
        PAPERS_DIR,
        EXTRACTED_DIR,
        ANALYSIS_DIR,
        DRAFTS_DIR,
        LOGS_DIR
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    return directories

def check_environment():
    """Check if all environment requirements are met."""
    from .config import GEMINI_API_KEY
    
    issues = []
    
    # Check API key
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_google_gemini_api_key_here":
        issues.append("Gemini API key not configured in .env file")
    
    # Check directories
    try:
        create_directories()
    except Exception as e:
        issues.append(f"Cannot create directories: {e}")
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append(f"Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}")
    
    return issues

# Initialize logging when package is imported
logger = setup_logging()

# Log package initialization
logger.info(f"🚀 Automated Research Review System v{__version__} initialized")
logger.info(f"📂 Project root: {PROJECT_ROOT}")

# Check environment and log warnings
env_issues = check_environment()
for issue in env_issues:
    logger.warning(f"⚠️ {issue}")

# Define what gets imported with "from package import *"
__all__ = [
    # Version info
    "__version__",
    "__author__",
    
    # Core classes
    "PaperSearcher",
    "TextExtractor", 
    "PaperAnalyzer",
    "DraftGenerator",
    
    # Configuration
    "BASE_DIR",
    "DATA_DIR",
    "PAPERS_DIR",
    "EXTRACTED_DIR",
    "ANALYSIS_DIR",
    "DRAFTS_DIR",
    "LOGS_DIR",
    "GEMINI_API_KEY",
    "MAX_PAPERS",
    
    # Utilities
    "setup_logging",
    "count_tokens",
    "chunk_text",
    "safe_json_loads",
    "sanitize_filename",
    "format_progress_message",
    "create_directories",
    "check_environment"
]