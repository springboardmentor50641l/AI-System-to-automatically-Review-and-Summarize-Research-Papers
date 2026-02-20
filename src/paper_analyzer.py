#!/usr/bin/env python3
"""
Paper Analyzer Module
Milestone 2: Performs semantic sectioning and cross-paper analysis.
UPDATED: Uses new google.genai package with correct model names.
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from google import genai  # NEW: Import from google.genai
from google.genai import types  # NEW: Import types for configuration
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from loguru import logger

# Local imports
from config import (
    GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TEMPERATURE,
    EXTRACTED_DIR, ANALYSIS_DIR, SECTION_ONTOLOGY,
    SECTIONING_PROMPT, ANALYSIS_PROMPT, COMPARISON_PROMPT,
    AVAILABLE_MODELS
)
from utils import (
    setup_logging, safe_json_loads, chunk_text, count_tokens,
    format_progress_message
)

# Setup logging
logger = setup_logging()

# Configure Gemini with new client
if not GEMINI_API_KEY:
    logger.error("❌ GEMINI_API_KEY not set. Please check your .env file.")
    logger.error("Get your API key from: https://makersuite.google.com/app/apikey")
    sys.exit(1)

try:
    # NEW: Initialize the new client
    client = genai.Client(api_key=GEMINI_API_KEY)
    logger.info(f"✅ Gemini client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Gemini client: {e}")
    sys.exit(1)

class AnalysisError(Exception):
    """Custom exception for analysis errors."""
    pass

class PaperAnalyzer:
    """Handles semantic analysis of research papers using new Gemini API."""
    
    def __init__(self):
        self.client = client
        # Use the correct model name from config
        self.model = GEMINI_MODEL
        logger.info(f"Using Gemini model: {self.model}")
        
        # Available models from debug output
        self.model_fallbacks = AVAILABLE_MODELS
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def section_paper(self, text: str) -> Dict[str, str]:
        """
        Use Gemini to semantically section the paper.
        
        Args:
            text: Normalized paper text
            
        Returns:
            Dictionary mapping section names to content
        """
        logger.info("Performing semantic sectioning")
        
        if not text or len(text.strip()) < 100:
            logger.warning("Text too short for sectioning")
            return {section: "" for section in SECTION_ONTOLOGY}
        
        # Check token count and truncate if needed
        token_count = count_tokens(text)
        logger.debug(f"Token count: {token_count}")
        
        if token_count > 28000:
            logger.warning(f"Text too long ({token_count} tokens), truncating")
            text = text[:100000]  # Rough truncation
        
        # Prepare prompt
        sections_str = ", ".join(SECTION_ONTOLOGY)
        prompt = SECTIONING_PROMPT.format(sections=sections_str, text=text)
        
        # Try different models if one fails
        models_to_try = [self.model] + self.model_fallbacks
        
        for model_name in models_to_try:
            try:
                logger.debug(f"Trying model: {model_name}")
                
                # NEW: Use the new API format
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=8192,
                    )
                )
                
                if not response.text:
                    logger.warning(f"Empty response from {model_name}")
                    continue
                
                # Parse response
                sections = safe_json_loads(response.text)
                
                # Validate sections
                for section in SECTION_ONTOLOGY:
                    if section not in sections:
                        sections[section] = ""
                
                non_empty = len([v for v in sections.values() if v])
                logger.success(f"Sectioned paper into {non_empty} non-empty sections using {model_name}")
                return sections
                
            except Exception as e:
                logger.debug(f"Model {model_name} failed: {e}")
                continue
        
        # If all models fail, return empty sections
        logger.error("All models failed for sectioning")
        return {section: "" for section in SECTION_ONTOLOGY}
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=5)
    )
    def extract_insights(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract key insights from paper sections.
        
        Args:
            sections: Sectioned paper content
            
        Returns:
            Dictionary with insights
        """
        logger.info("Extracting insights from paper")
        
        if not any(sections.values()):
            logger.warning("No section content to analyze")
            return self._get_default_insights()
        
        # Prepare sections for prompt
        sections_summary = {}
        for key, value in sections.items():
            if value:
                if len(value) > 3000:
                    sections_summary[key] = value[:3000] + "..."
                else:
                    sections_summary[key] = value
        
        prompt = ANALYSIS_PROMPT.format(sections=json.dumps(sections_summary, indent=2))
        
        models_to_try = [self.model] + self.model_fallbacks
        
        for model_name in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=8192,
                    )
                )
                
                if not response.text:
                    continue
                
                insights = safe_json_loads(response.text)
                
                # Ensure required fields
                required_fields = ["key_findings", "contributions", "limitations", "future_work"]
                for field in required_fields:
                    if field not in insights or not insights[field]:
                        insights[field] = []
                
                logger.success(f"Extracted {len(insights.get('key_findings', []))} key findings")
                return insights
                
            except Exception as e:
                logger.debug(f"Insight extraction with {model_name} failed: {e}")
                continue
        
        return self._get_default_insights()
    
    def _get_default_insights(self) -> Dict[str, Any]:
        """Return default insights when analysis fails."""
        return {
            "key_findings": ["Analysis temporarily unavailable - API issue"],
            "contributions": [],
            "limitations": [],
            "future_work": []
        }
    
    def analyze_paper(self, extracted_json: Path) -> Dict[str, Any]:
        """
        Complete analysis pipeline for a single paper.
        """
        logger.info(format_progress_message("analyze", f"Analyzing: {extracted_json.name}"))
        
        try:
            with open(extracted_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            normalized_text = data.get("normalized_text", "")
            if not normalized_text:
                logger.warning(f"No normalized text found in {extracted_json.name}")
                return self._create_failed_analysis(data, "No text content")
            
            # Perform sectioning
            sections = self.section_paper(normalized_text)
            
            # Extract insights
            insights = self.extract_insights(sections)
            
            analysis = {
                "pdf_path": data.get("pdf_path"),
                "pdf_name": data.get("pdf_name"),
                "file_hash": data.get("file_hash"),
                "metadata": data.get("metadata", {}),
                "sections": sections,
                "insights": insights,
                "analysis_status": "success",
                "stats": {
                    "total_sections": len([v for v in sections.values() if v]),
                    "key_findings_count": len(insights.get("key_findings", [])),
                    "text_length": len(normalized_text),
                    "analysis_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            }
            
            logger.success(f"Analysis complete for {extracted_json.stem}")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze {extracted_json.name}: {e}")
            return self._create_failed_analysis({"pdf_name": extracted_json.name}, str(e))
    
    def _create_failed_analysis(self, data: Dict, error_msg: str) -> Dict:
        """Create a failed analysis entry."""
        return {
            "pdf_path": data.get("pdf_path", "Unknown"),
            "pdf_name": data.get("pdf_name", "Unknown"),
            "analysis_status": "failed",
            "error": error_msg,
            "sections": {},
            "insights": self._get_default_insights(),
            "stats": {
                "total_sections": 0,
                "key_findings_count": 0,
                "analysis_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    
    def save_analysis(self, analysis: Dict, output_dir: Path) -> Path:
        """Save analysis to JSON file."""
        pdf_name = Path(analysis.get("pdf_path", "unknown")).stem
        safe_name = "".join(c for c in pdf_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        out_path = output_dir / f"{safe_name}_analysis.json"
        
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved analysis: {out_path.name}")
        return out_path
    
    def process_all_papers(self, extracted_dir: Path = EXTRACTED_DIR) -> List[Path]:
        """Process all extracted papers."""
        json_files = list(extracted_dir.glob("*.json"))
        
        if not json_files:
            logger.warning(f"No extracted text files found in {extracted_dir}")
            return []
        
        logger.info(f"Found {len(json_files)} papers to analyze")
        analysis_paths = []
        analyses = []
        
        for i, json_path in enumerate(json_files, 1):
            logger.info(f"Processing paper {i}/{len(json_files)}: {json_path.name}")
            try:
                analysis = self.analyze_paper(json_path)
                out_path = self.save_analysis(analysis, ANALYSIS_DIR)
                analysis_paths.append(str(out_path))
                
                if analysis.get("analysis_status") == "success":
                    analyses.append(analysis)
                
                # Delay to avoid rate limits
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to analyze {json_path.name}: {e}")
        
        # Perform cross-paper comparison if multiple papers
        if len(analyses) >= 2:
            try:
                topic = "research_topic"
                comparison = self.compare_papers(analyses, topic)
                
                comp_path = ANALYSIS_DIR / "cross_paper_comparison.json"
                with open(comp_path, 'w', encoding='utf-8') as f:
                    json.dump(comparison, f, indent=2, ensure_ascii=False)
                
                logger.success(f"Saved cross-paper comparison: {comp_path}")
                
            except Exception as e:
                logger.error(f"Cross-paper comparison failed: {e}")
        
        return analysis_paths
    
    def compare_papers(self, analyses: List[Dict], topic: str) -> Dict[str, Any]:
        """Compare multiple papers."""
        logger.info("Performing cross-paper comparison")
        
        if len(analyses) < 2:
            return {"error": "Insufficient papers for comparison", "num_papers": len(analyses)}
        
        try:
            comparison_data = []
            for analysis in analyses:
                paper_summary = {
                    "title": analysis.get("metadata", {}).get("title", "Unknown"),
                    "key_findings": analysis.get("insights", {}).get("key_findings", [])[:3],
                    "methodology": analysis.get("sections", {}).get("methodology", "")[:1000],
                    "conclusion": analysis.get("sections", {}).get("conclusion", "")[:500]
                }
                comparison_data.append(paper_summary)
            
            prompt = COMPARISON_PROMPT.format(
                topic=topic,
                analyses=json.dumps(comparison_data, indent=2)
            )
            
            models_to_try = [self.model] + self.model_fallbacks
            
            for model_name in models_to_try:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.1,
                            max_output_tokens=8192,
                        )
                    )
                    
                    if response.text:
                        comparison = safe_json_loads(response.text)
                        comparison["num_papers"] = len(analyses)
                        comparison["topic"] = topic
                        comparison["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        return comparison
                        
                except Exception as e:
                    logger.debug(f"Comparison with {model_name} failed: {e}")
                    continue
            
            return self._get_default_comparison(len(analyses), topic)
            
        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            return self._get_default_comparison(len(analyses), topic)
    
    def _get_default_comparison(self, num_papers: int, topic: str) -> Dict:
        """Return default comparison."""
        return {
            "common_methodologies": ["Unable to extract methodologies"],
            "divergent_findings": ["Analysis temporarily unavailable"],
            "unique_contributions": [],
            "research_gaps": [],
            "summary": f"Cross-paper analysis for {num_papers} papers on '{topic}' is temporarily unavailable.",
            "num_papers": num_papers,
            "topic": topic,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze extracted research papers")
    parser.add_argument("json_path", nargs="?", help="Path to specific extracted JSON file")
    parser.add_argument("--dir", help="Directory with extracted JSON files")
    parser.add_argument("--topic", help="Research topic for comparison")
    
    args = parser.parse_args()
    
    try:
        analyzer = PaperAnalyzer()
    except Exception as e:
        logger.error(f"Failed to initialize analyzer: {e}")
        sys.exit(1)
    
    try:
        if args.json_path:
            json_path = Path(args.json_path)
            if not json_path.exists():
                logger.error(f"File not found: {json_path}")
                sys.exit(1)
            
            analysis = analyzer.analyze_paper(json_path)
            out_path = analyzer.save_analysis(analysis, ANALYSIS_DIR)
            print(f"\n✅ Analysis saved to: {out_path}")
            
        else:
            input_dir = Path(args.dir) if args.dir else EXTRACTED_DIR
            analysis_paths = analyzer.process_all_papers(input_dir)
            
            print("\n" + "="*50)
            print(f"📊 Analysis Results")
            print("="*50)
            print(f"Total papers processed: {len(analysis_paths)}")
            for path in analysis_paths:
                print(f"  ✅ {Path(path).name}")
            print("="*50)
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()