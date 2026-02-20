#!/usr/bin/env python3
"""
Draft Generator Module
Milestone 3: Generates structured research review drafts.
UPDATED: Uses new google.genai package.
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

# Local imports
from config import (
    GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TEMPERATURE,
    ANALYSIS_DIR, DRAFTS_DIR, DRAFT_PROMPT, AVAILABLE_MODELS
)
from utils import (
    setup_logging, safe_json_loads, sanitize_filename,
    format_progress_message
)

# Setup logging
logger = setup_logging()

# Configure Gemini
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not set. Please check your .env file.")
    sys.exit(1)

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    logger.info(f"✅ Gemini client initialized")
except Exception as e:
    logger.error(f"Failed to initialize Gemini client: {e}")
    sys.exit(1)

class DraftGenerationError(Exception):
    """Custom exception for draft generation errors."""
    pass

class DraftGenerator:
    """Handles generation of research review drafts."""
    
    def __init__(self):
        self.client = client
        self.model = GEMINI_MODEL
        self.model_fallbacks = AVAILABLE_MODELS
    
    def load_analyses(self, analysis_dir: Path = ANALYSIS_DIR) -> List[Dict]:
        """Load all analysis JSON files."""
        analysis_files = list(analysis_dir.glob("*_analysis.json"))
        
        if not analysis_files:
            logger.warning(f"No analysis files found in {analysis_dir}")
            return []
        
        logger.info(f"Found {len(analysis_files)} analysis files")
        
        analyses = []
        for file_path in analysis_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    analysis = json.load(f)
                if analysis.get("analysis_status") == "success":
                    analyses.append(analysis)
            except Exception as e:
                logger.error(f"Failed to load {file_path.name}: {e}")
        
        return analyses
    
    def prepare_analysis_data(self, analyses: List[Dict]) -> Dict:
        """Prepare analysis data for the prompt."""
        prepared = {
            "papers": [],
            "num_papers": len(analyses)
        }
        
        for i, analysis in enumerate(analyses, 1):
            paper_data = {
                "title": analysis.get("metadata", {}).get("title", f"Paper {i}"),
                "authors": analysis.get("metadata", {}).get("authors", [])[:3],
                "year": analysis.get("metadata", {}).get("year", "Unknown"),
                "key_findings": analysis.get("insights", {}).get("key_findings", [])[:5],
                "methodology_summary": analysis.get("sections", {}).get("methodology", "")[:1000],
                "results_summary": analysis.get("sections", {}).get("results", "")[:1000]
            }
            prepared["papers"].append(paper_data)
        
        return prepared
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def generate_draft(self, analysis_data: Dict, topic: str) -> str:
        """Generate research review draft."""
        logger.info(format_progress_message("draft", "Generating research draft"))
        
        prompt = DRAFT_PROMPT.format(
            topic=topic,
            analysis_data=json.dumps(analysis_data, indent=2)
        )
        
        models_to_try = [self.model] + self.model_fallbacks
        
        for model_name in models_to_try:
            try:
                logger.debug(f"Trying model: {model_name}")
                
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=8192,
                    )
                )
                
                if response.text:
                    logger.success(f"Draft generated with {model_name}")
                    return response.text
                    
            except Exception as e:
                logger.debug(f"Model {model_name} failed: {e}")
                continue
        
        raise DraftGenerationError("All models failed to generate draft")
    
    def save_draft(self, draft: str, topic: str, output_dir: Path = DRAFTS_DIR) -> Path:
        """Save draft to text file."""
        safe_topic = sanitize_filename(topic)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_topic}_review_draft_{timestamp}.txt"
        
        out_path = output_dir / filename
        
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(draft)
        
        logger.info(f"Draft saved: {out_path.name}")
        return out_path
    
    def generate_review(self, topic: str) -> Dict[str, Any]:
        """Complete draft generation pipeline."""
        logger.info(f"Starting draft generation for topic: '{topic}'")
        
        analyses = self.load_analyses()
        if not analyses:
            return {
                "success": False,
                "message": "No successful analysis files found",
                "draft": None,
                "draft_path": None
            }
        
        try:
            analysis_data = self.prepare_analysis_data(analyses)
            draft = self.generate_draft(analysis_data, topic)
            draft_path = self.save_draft(draft, topic)
            
            return {
                "success": True,
                "message": f"Successfully generated draft from {len(analyses)} papers",
                "draft": draft,
                "draft_path": str(draft_path),
                "num_papers": len(analyses)
            }
            
        except Exception as e:
            logger.error(f"Draft generation failed: {e}")
            return {
                "success": False,
                "message": f"Draft generation failed: {e}",
                "draft": None,
                "draft_path": None
            }
    
    def format_draft_for_display(self, draft: str) -> str:
        """Format draft for display in Gradio UI."""
        lines = draft.split('\n')
        formatted = []
        
        for line in lines:
            if line.strip().startswith('ABSTRACT'):
                formatted.append('\n📝 ' + line)
            elif line.strip().startswith('METHODS'):
                formatted.append('\n🔬 ' + line)
            elif line.strip().startswith('RESULTS'):
                formatted.append('\n📊 ' + line)
            elif line.strip().startswith('DISCUSSION'):
                formatted.append('\n💭 ' + line)
            elif line.strip().startswith('APA REFERENCES'):
                formatted.append('\n📚 ' + line)
            else:
                formatted.append(line)
        
        return '\n'.join(formatted)

def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate research review draft")
    parser.add_argument("topic", help="Research topic")
    
    args = parser.parse_args()
    
    generator = DraftGenerator()
    
    try:
        result = generator.generate_review(args.topic)
        
        print("\n" + "="*60)
        print(f"Topic: {args.topic}")
        print(f"Status: {'✅ Success' if result['success'] else '❌ Failed'}")
        print(f"Message: {result['message']}")
        
        if result['success']:
            print(f"Papers analyzed: {result['num_papers']}")
            print(f"Draft saved: {result['draft_path']}")
            
            print("\n" + "="*60)
            print("DRAFT PREVIEW:")
            print("="*60)
            print(generator.format_draft_for_display(result['draft'][:1000]))
            print("...")
        
        print("="*60)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()