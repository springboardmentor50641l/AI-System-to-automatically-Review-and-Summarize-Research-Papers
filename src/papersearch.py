#!/usr/bin/env python3
"""
Paper Search and Download Module
Milestone 1: Searches Semantic Scholar and downloads PDFs.
Strictly ensures only valid PDF files are saved.
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

# Local imports
from config import PAPERS_DIR, MAX_PAPERS, SEMANTIC_SCHOLAR_API_KEY
from utils import setup_logging, sanitize_filename, format_progress_message

# Setup logging
logger = setup_logging()

class PaperSearchError(Exception):
    """Custom exception for paper search errors."""
    pass

class PaperSearcher:
    """Handles paper search and download operations with PDF validation."""
    
    def __init__(self):
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; AcademicResearchBot/1.0)",
            "Accept": "application/json"
        }
        
        # Add API key if available
        if SEMANTIC_SCHOLAR_API_KEY:
            self.headers["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def validate_pdf(self, file_path: Path) -> bool:
        """
        Strictly validate that a file is a genuine PDF.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if valid PDF, False otherwise
        """
        if not file_path.exists():
            logger.debug(f"File does not exist: {file_path}")
            return False
        
        # Check 1: File extension must be .pdf
        if file_path.suffix.lower() != '.pdf':
            logger.debug(f"Invalid extension: {file_path.suffix}")
            return False
        
        # Check 2: File must not be empty
        if file_path.stat().st_size == 0:
            logger.debug(f"File is empty: {file_path}")
            return False
        
        # Check 3: File must start with PDF header (%PDF)
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                is_pdf = header == b'%PDF'
                
                if not is_pdf:
                    logger.debug(f"Invalid PDF header: {header}")
                
                return is_pdf
        except Exception as e:
            logger.debug(f"Error reading file header: {e}")
            return False
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def search_papers(self, topic: str, limit: int = MAX_PAPERS) -> List[Dict]:
        """
        Search for papers on Semantic Scholar.
        
        Args:
            topic: Research topic to search for
            limit: Maximum number of papers to return
            
        Returns:
            List of paper metadata dictionaries
        """
        logger.info(f"Searching for papers on topic: '{topic}'")
        
        url = f"{self.base_url}/paper/search"
        params = {
            "query": topic,
            "limit": limit * 2,  # Fetch more to filter those with PDFs
            "fields": "title,abstract,url,openAccessPdf,year,authors,venue,citationCount"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            papers = []
            for paper in data.get("data", []):
                # Check for open access PDF
                pdf_info = paper.get("openAccessPdf")
                if pdf_info and pdf_info.get("url"):
                    paper_data = {
                        "title": paper.get("title", "Untitled"),
                        "abstract": paper.get("abstract", ""),
                        "pdf_url": pdf_info["url"],
                        "url": paper.get("url", ""),
                        "year": paper.get("year"),
                        "authors": [a.get("name") for a in paper.get("authors", [])],
                        "venue": paper.get("venue"),
                        "citation_count": paper.get("citationCount", 0)
                    }
                    papers.append(paper_data)
                    
                    if len(papers) >= limit:
                        break
            
            logger.success(f"Found {len(papers)} papers with PDF links")
            return papers
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Search request failed: {e}")
            raise PaperSearchError(f"Failed to search papers: {e}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def download_pdf(self, paper: Dict, save_dir: Path) -> Optional[Path]:
        """
        Download PDF from paper URL and validate it.
        
        Args:
            paper: Paper metadata dictionary
            save_dir: Directory to save PDF
            
        Returns:
            Path to downloaded PDF or None if failed/invalid
        """
        # Create safe filename
        safe_title = sanitize_filename(paper["title"])
        pdf_path = save_dir / f"{safe_title}.pdf"
        
        # Skip if already downloaded and valid
        if pdf_path.exists():
            if self.validate_pdf(pdf_path):
                logger.info(f"Valid PDF already exists: {pdf_path.name}")
                return pdf_path
            else:
                logger.warning(f"Existing file is not a valid PDF, re-downloading: {pdf_path.name}")
                pdf_path.unlink()  # Delete invalid file
        
        logger.info(f"Downloading: {paper['title'][:50]}...")
        
        try:
            # Download with progress tracking
            response = self.session.get(
                paper["pdf_url"],
                stream=True,
                timeout=60,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()
            
            # Check content type if available
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' not in content_type.lower() and content_type:
                logger.warning(f"Unexpected content type: {content_type}")
                # Still try to download, validation will catch it
            
            # Download file
            with open(pdf_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Strict validation of downloaded file
            if self.validate_pdf(pdf_path):
                logger.success(f"Downloaded and validated PDF: {pdf_path.name}")
                return pdf_path
            else:
                logger.error(f"Downloaded file is not a valid PDF: {pdf_path.name}")
                pdf_path.unlink()  # Delete invalid file
                return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Download failed for {paper['title']}: {e}")
            
            # Clean up partial download
            if pdf_path.exists():
                pdf_path.unlink()
            
            return None
    
    def save_metadata(self, papers: List[Dict], topic: str, save_dir: Path):
        """
        Save paper metadata to JSON file.
        
        Args:
            papers: List of paper metadata
            topic: Search topic
            save_dir: Directory to save metadata
        """
        metadata = {
            "topic": topic,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_papers": len(papers),
            "papers": papers
        }
        
        safe_topic = sanitize_filename(topic)
        meta_path = save_dir / f"{safe_topic}_metadata.json"
        
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Metadata saved: {meta_path}")
        return meta_path
    
    def process_topic(self, topic: str) -> Dict:
        """
        Complete pipeline for a topic: search, download, validate, save metadata.
        Strictly ensures only valid PDFs are kept.
        
        Args:
            topic: Research topic
            
        Returns:
            Dictionary with results summary
        """
        logger.info(format_progress_message("search", f"Searching for: {topic}"))
        
        # Search papers
        papers = self.search_papers(topic)
        if not papers:
            return {
                "success": False,
                "message": "No papers found with PDF links",
                "papers": []
            }
        
        # Download and validate PDFs
        downloaded_papers = []
        for paper in papers:
            logger.info(format_progress_message("download", f"Downloading: {paper['title'][:50]}..."))
            
            pdf_path = self.download_pdf(paper, PAPERS_DIR)
            if pdf_path:
                paper["local_path"] = str(pdf_path)
                downloaded_papers.append(paper)
                logger.info(f"✅ Valid PDF saved: {pdf_path.name}")
            else:
                logger.warning(f"❌ Failed to download valid PDF for: {paper['title'][:50]}...")
            
            # Small delay to be respectful to servers
            time.sleep(1)
        
        # Save metadata only for successfully downloaded papers
        if downloaded_papers:
            self.save_metadata(downloaded_papers, topic, PAPERS_DIR)
            
            return {
                "success": True,
                "message": f"Successfully downloaded {len(downloaded_papers)} valid PDFs",
                "papers": downloaded_papers
            }
        else:
            return {
                "success": False,
                "message": "Failed to download any valid PDFs",
                "papers": []
            }

def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python papersearch.py \"<research topic>\"")
        print("Example: python papersearch.py \"machine learning transformers\"")
        sys.exit(1)
    
    topic = sys.argv[1]
    
    try:
        searcher = PaperSearcher()
        result = searcher.process_topic(topic)
        
        print("\n" + "="*50)
        print(f"Topic: {topic}")
        print(f"Status: {'✅ Success' if result['success'] else '❌ Failed'}")
        print(f"Message: {result['message']}")
        
        if result['papers']:
            print("\nDownloaded Valid PDFs:")
            for i, paper in enumerate(result['papers'], 1):
                print(f"{i}. {paper['title']}")
                print(f"   📍 {paper['local_path']}")
        
        print("="*50)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()