#!/usr/bin/env python3
"""
Text Extraction Module
Milestone 2: Extracts and normalizes text from PDFs.
Strictly processes only valid PDF files.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Optional
import fitz  # PyMuPDF
from loguru import logger

# Local imports
from config import PAPERS_DIR, EXTRACTED_DIR
from utils import setup_logging, generate_file_hash, sanitize_filename

# Setup logging
logger = setup_logging()

class TextExtractionError(Exception):
    """Custom exception for text extraction errors."""
    pass

class TextExtractor:
    """Handles PDF text extraction and normalization."""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def validate_pdf(self, file_path: Path) -> bool:
        """
        Strictly validate that a file is a genuine PDF before processing.
        
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
            logger.debug(f"Invalid extension for extraction: {file_path.suffix}")
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
                    logger.debug(f"Invalid PDF header for extraction: {header}")
                
                return is_pdf
        except Exception as e:
            logger.debug(f"Error reading file header: {e}")
            return False
    
    def extract_raw_text(self, pdf_path: Path) -> str:
        """
        Extract raw text from PDF using PyMuPDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text as string
        """
        logger.debug(f"Extracting text from: {pdf_path.name}")
        
        # Validate PDF before extraction
        if not self.validate_pdf(pdf_path):
            raise TextExtractionError(f"File is not a valid PDF: {pdf_path}")
        
        try:
            doc = fitz.open(pdf_path)
            pages = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                
                if text.strip():
                    pages.append(text)
                else:
                    logger.warning(f"Page {page_num + 1} has no extractable text")
            
            doc.close()
            
            if not pages:
                raise TextExtractionError("No text extracted from PDF")
            
            full_text = "\n\n".join(pages)
            logger.debug(f"Extracted {len(pages)} pages, ~{len(full_text)} characters")
            
            return full_text
            
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            raise TextExtractionError(f"Text extraction failed: {e}")
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize extracted text by cleaning artifacts.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Normalized text
        """
        logger.debug("Normalizing extracted text")
        
        # Remove soft hyphens and fix broken words
        text = text.replace("-\n", "")
        
        # Fix common PDF extraction artifacts
        replacements = [
            ("\f", "\n"),  # Form feeds to newlines
            ("\r\n", "\n"),  # Windows to Unix newlines
            ("\r", "\n"),  # Old Mac to Unix newlines
            ("  ", " "),  # Double spaces
            ("\n ", "\n"),  # Space after newline
            (" \n", "\n"),  # Space before newline
        ]
        
        for old, new in replacements:
            text = text.replace(old, new)
        
        # Normalize multiple newlines
        lines = []
        empty_count = 0
        
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped:
                lines.append(stripped)
                empty_count = 0
            else:
                empty_count += 1
                if empty_count == 1:  # Keep one empty line between paragraphs
                    lines.append("")
        
        # Remove leading/trailing empty lines
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        
        normalized = "\n".join(lines)
        logger.debug(f"Normalized text length: {len(normalized)} characters")
        
        return normalized
    
    def extract_metadata(self, pdf_path: Path) -> Dict:
        """
        Extract PDF metadata.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with PDF metadata
        """
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata
            doc.close()
            
            return {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "keywords": metadata.get("keywords", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", "")
            }
        except Exception as e:
            logger.warning(f"Could not extract metadata: {e}")
            return {}
    
    def process_pdf(self, pdf_path: Path) -> Dict:
        """
        Complete processing pipeline for a single PDF.
        Only processes valid PDF files.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted data
        """
        logger.info(f"Processing PDF: {pdf_path.name}")
        
        # Validate PDF before processing
        if not self.validate_pdf(pdf_path):
            raise TextExtractionError(f"Invalid or corrupted PDF file: {pdf_path}")
        
        # Extract metadata
        metadata = self.extract_metadata(pdf_path)
        
        # Extract and normalize text
        raw_text = self.extract_raw_text(pdf_path)
        normalized_text = self.normalize_text(raw_text)
        
        # Generate file hash for deduplication
        file_hash = generate_file_hash(pdf_path)
        
        result = {
            "pdf_path": str(pdf_path),
            "pdf_name": pdf_path.name,
            "file_hash": file_hash,
            "metadata": metadata,
            "raw_text": raw_text,
            "normalized_text": normalized_text,
            "stats": {
                "raw_length": len(raw_text),
                "normalized_length": len(normalized_text),
                "raw_lines": len(raw_text.split("\n")),
                "normalized_lines": len(normalized_text.split("\n"))
            }
        }
        
        logger.success(f"Processed {pdf_path.name}: {result['stats']['normalized_length']} chars")
        return result
    
    def save_extracted(self, data: Dict, output_dir: Path) -> Path:
        """
        Save extracted data to JSON file.
        
        Args:
            data: Extracted data dictionary
            output_dir: Output directory
            
        Returns:
            Path to saved JSON file
        """
        # Create output filename from PDF name
        pdf_name = Path(data["pdf_path"]).stem
        safe_name = sanitize_filename(pdf_name)
        out_path = output_dir / f"{safe_name}.json"
        
        # Save with pretty printing
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved extracted text: {out_path}")
        return out_path
    
    def process_all_pdfs(self, pdf_dir: Path = PAPERS_DIR) -> list:
        """
        Process all valid PDFs in a directory.
        Skips any non-PDF files or invalid PDFs.
        
        Args:
            pdf_dir: Directory containing PDFs
            
        Returns:
            List of paths to saved JSON files
        """
        all_files = list(pdf_dir.glob("*"))
        pdf_files = []
        
        # Filter only valid PDFs
        for file_path in all_files:
            if self.validate_pdf(file_path):
                pdf_files.append(file_path)
            else:
                if file_path.suffix.lower() == '.pdf':
                    logger.warning(f"Skipping invalid PDF: {file_path.name}")
                else:
                    logger.debug(f"Skipping non-PDF file: {file_path.name}")
        
        if not pdf_files:
            logger.warning(f"No valid PDF files found in {pdf_dir}")
            return []
        
        logger.info(f"Found {len(pdf_files)} valid PDFs to process")
        saved_files = []
        
        for pdf_path in pdf_files:
            try:
                data = self.process_pdf(pdf_path)
                out_path = self.save_extracted(data, EXTRACTED_DIR)
                saved_files.append(str(out_path))
            except Exception as e:
                logger.error(f"Failed to process {pdf_path.name}: {e}")
        
        logger.success(f"Successfully processed {len(saved_files)}/{len(pdf_files)} valid PDFs")
        return saved_files

def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract text from research PDFs")
    parser.add_argument("pdf_path", nargs="?", help="Path to specific PDF file")
    parser.add_argument("--dir", help="Directory containing PDFs (default: data/papers/)")
    parser.add_argument("--output", help="Output directory (default: data/extracted_text/)")
    
    args = parser.parse_args()
    
    extractor = TextExtractor()
    
    try:
        if args.pdf_path:
            # Process single PDF
            pdf_path = Path(args.pdf_path)
            if not pdf_path.exists():
                logger.error(f"PDF not found: {pdf_path}")
                sys.exit(1)
            
            # Validate before processing
            if not extractor.validate_pdf(pdf_path):
                logger.error(f"File is not a valid PDF: {pdf_path}")
                sys.exit(1)
            
            data = extractor.process_pdf(pdf_path)
            out_path = extractor.save_extracted(data, EXTRACTED_DIR)
            print(f"\n✅ Text extracted and saved to: {out_path}")
            
        else:
            # Process all PDFs
            pdf_dir = Path(args.dir) if args.dir else PAPERS_DIR
            saved_files = extractor.process_all_pdfs(pdf_dir)
            
            print("\n" + "="*50)
            print(f"Processed {len(saved_files)} valid PDFs")
            for f in saved_files:
                print(f"  📄 {Path(f).name}")
            print("="*50)
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()