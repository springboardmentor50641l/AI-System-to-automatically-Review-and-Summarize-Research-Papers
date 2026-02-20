"""
Configuration module for the Automated Research Review System.
Handles all configuration settings, paths, and constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Base paths - Points to project root (parent of src/)
BASE_DIR = Path(__file__).parent.parent.absolute()
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
PAPERS_DIR = DATA_DIR / "papers"
EXTRACTED_DIR = DATA_DIR / "extracted_text"
ANALYSIS_DIR = DATA_DIR / "analysis"
DRAFTS_DIR = DATA_DIR / "drafts"

for directory in [PAPERS_DIR, EXTRACTED_DIR, ANALYSIS_DIR, DRAFTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not found in environment variables")

SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")

# Application Settings - FIX: Add these missing variables
MAX_PAPERS = int(os.getenv("MAX_PAPERS", "3"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Model Configuration - Updated model names
AVAILABLE_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
]

# Use the latest stable model
GEMINI_MODEL = "gemini-2.0-flash"  # Changed from gemini-1.5-pro
GEMINI_TEMPERATURE = 0.1
MAX_TOKENS = 30000

# Section Ontology for Paper Analysis
SECTION_ONTOLOGY = [
    "abstract",
    "introduction",
    "related_work",
    "methodology",
    "experiments",
    "results",
    "discussion",
    "conclusion",
    "references"
]

# Prompt Templates
SECTIONING_PROMPT = """You are an expert at parsing research papers. Given the full text of a paper, divide it into the following logical sections. Return ONLY a JSON object with these keys, each containing the exact text that belongs to that section. Do not summarize or rephrase. If a section is missing, use an empty string.

Keys: {sections}

Text:
{text}

JSON:"""

ANALYSIS_PROMPT = """You are analyzing research papers. Based on the provided sections, extract the key findings and contributions.

Paper Sections:
{sections}

Return a JSON object with:
1. key_findings: list of 3-5 main findings
2. contributions: list of main contributions
3. limitations: any mentioned limitations
4. future_work: suggested future research

JSON:"""

COMPARISON_PROMPT = """Compare the following research papers on the topic "{topic}".

Papers analysis:
{analyses}

Generate a comprehensive comparison covering:
1. Common methodologies used
2. Divergent findings or contradictions
3. Unique contributions of each paper
4. Research gaps identified

Return as JSON with these keys:
- common_methodologies
- divergent_findings
- unique_contributions
- research_gaps
- summary

JSON:"""

DRAFT_PROMPT = """You are an expert research assistant. Based on the following analysis of multiple research papers on "{topic}", generate a structured research review draft.

Analysis data:
{analysis_data}

Generate a draft with these sections:

1. ABSTRACT (maximum 100 words)
   Summarize the key findings and contributions across all papers.

2. METHODS COMPARISON
   Compare the methodologies used across papers. Highlight similarities, differences, and innovative approaches.

3. RESULTS SYNTHESIS
   Synthesize the main results from all papers. Identify consistent findings and any contradictions.

4. DISCUSSION
   Discuss the implications of the findings, limitations, and future research directions.

5. APA REFERENCES
   List all references in proper APA 7th edition format.

Return the draft as plain text with clear section headings."""