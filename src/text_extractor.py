"""
text_extractor.py
Milestone 2: Extract and process text from PDF documents
Handles regular PDFs, scanned PDFs (OCR), and section segmentation
"""

import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image
import io
import os
import re
import json
import nltk
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

try:
    from src.config import Config
    from src.utils import create_filename
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.config import Config
    from src.utils import create_filename

class TextExtractor:
    """Extract text from PDFs with multiple fallback methods"""
    
    def __init__(self):
        """Initialize extractor with configuration"""
        self.text_dir = Config.DATA_DIR / "extracted_text"
        self.text_dir.mkdir(exist_ok=True)
        
        # Section patterns for academic papers
        self.section_patterns = {
            'abstract': r'^(abstract|summary)\b',
            'introduction': r'^1\.?\s*introduction|\nintroduction\b',
            'methodology': r'^(2\.?\s*)?(methodology|methods|materials and methods)\b',
            'results': r'^(3\.?\s*)?(results|findings)\b',
            'discussion': r'^(4\.?\s*)?discussion\b',
            'conclusion': r'^(5\.?\s*)?(conclusion|conclusions)\b',
            'references': r'^(references|bibliography)\b'
        }
    
    def extract_with_pymupdf(self, pdf_path):
        """
        Extract text using PyMuPDF (fastest for text-based PDFs)
        Returns: List of pages with text and metadata
        """
        try:
            doc = fitz.open(pdf_path)
            pages_data = []
            
            print(f"📖 Extracting with PyMuPDF ({len(doc)} pages)...")
            
            for page_num in tqdm(range(len(doc)), desc="Pages"):
                page = doc.load_page(page_num)
                
                # Extract text
                text = page.get_text()
                
                # Extract page dimensions
                rect = page.rect
                
                pages_data.append({
                    'page_number': page_num + 1,
                    'text': text.strip(),
                    'method': 'pymupdf',
                    'page_width': rect.width,
                    'page_height': rect.height,
                    'has_images': len(page.get_images()) > 0
                })
            
            doc.close()
            return pages_data
            
        except Exception as e:
            print(f"PyMuPDF extraction failed: {e}")
            return []
    
    def extract_with_pdfplumber(self, pdf_path):
        """
        Extract text using pdfplumber (better for tables)
        """
        try:
            pages_data = []
            
            print("📖 Extracting with pdfplumber...")
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(tqdm(pdf.pages, desc="Pages"), 1):
                    text = page.extract_text()
                    
                    # Extract tables if any
                    tables = page.extract_tables()
                    table_text = ""
                    
                    for table in tables:
                        for row in table:
                            table_text += " | ".join([str(cell) if cell else "" for cell in row]) + "\n"
                    
                    pages_data.append({
                        'page_number': page_num,
                        'text': text.strip() if text else "",
                        'tables': table_text,
                        'method': 'pdfplumber'
                    })
            
            return pages_data
            
        except Exception as e:
            print(f"PDFPlumber extraction failed: {e}")
            return []
    
    def extract_with_ocr(self, pdf_path):
        """
        Extract text using OCR (for scanned PDFs)
        """
        try:
            doc = fitz.open(pdf_path)
            pages_data = []
            
            print("🔍 Using OCR for scanned PDF...")
            
            for page_num in tqdm(range(len(doc)), desc="OCR Pages"):
                page = doc.load_page(page_num)
                
                # Get image of page
                pix = page.get_pixmap()
                img_data = pix.tobytes("ppm")
                image = Image.open(io.BytesIO(img_data))
                
                # Perform OCR
                text = pytesseract.image_to_string(image)
                
                pages_data.append({
                    'page_number': page_num + 1,
                    'text': text.strip(),
                    'method': 'ocr',
                    'resolution': f"{pix.width}x{pix.height}"
                })
            
            doc.close()
            return pages_data
            
        except Exception as e:
            print(f"OCR extraction failed: {e}")
            return []
    
    def extract_text(self, pdf_path):
        """
        Main extraction method with fallback strategies
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            print(f"❌ PDF not found: {pdf_path}")
            return None
        
        print(f"\n{'='*60}")
        print(f"📄 Processing: {pdf_path.name}")
        print(f"{'='*60}")
        
        # Try PyMuPDF first (fastest)
        pages_data = self.extract_with_pymupdf(pdf_path)
        
        # If little text extracted, try pdfplumber
        total_text = sum(len(page['text']) for page in pages_data)
        if total_text < 1000 and len(pages_data) > 0:
            print("⚠️  Low text count, trying pdfplumber...")
            alt_data = self.extract_with_pdfplumber(pdf_path)
            
            # Use whichever extracted more text
            alt_text = sum(len(page['text']) for page in alt_data)
            if alt_text > total_text:
                pages_data = alt_data
        
        # If still little text, try OCR
        total_text = sum(len(page['text']) for page in pages_data)
        if total_text < 500 and len(pages_data) > 0:
            print("⚠️  Very low text, trying OCR...")
            ocr_data = self.extract_with_ocr(pdf_path)
            ocr_text = sum(len(page['text']) for page in ocr_data)
            
            if ocr_text > total_text:
                pages_data = ocr_data
        
        # Calculate statistics
        total_pages = len(pages_data)
        total_chars = sum(len(page['text']) for page in pages_data)
        total_words = sum(len(page['text'].split()) for page in pages_data)
        
        print(f"\n📊 Extraction Statistics:")
        print(f"   Pages: {total_pages}")
        print(f"   Characters: {total_chars:,}")
        print(f"   Words: {total_words:,}")
        print(f"   Method: {pages_data[0]['method'] if pages_data else 'None'}")
        
        return {
            'file_name': pdf_path.name,
            'file_path': str(pdf_path),
            'extraction_date': datetime.now().isoformat(),
            'total_pages': total_pages,
            'total_chars': total_chars,
            'total_words': total_words,
            'extraction_method': pages_data[0]['method'] if pages_data else 'failed',
            'pages': pages_data
        }
    
    def segment_into_sections(self, extracted_data):
        """
        Identify and segment paper into standard sections
        """
        if not extracted_data or 'pages' not in extracted_data:
            return {}
        
        # Combine all pages text
        full_text = "\n\n".join([page['text'] for page in extracted_data['pages']])
        
        sections = {
            'abstract': '',
            'introduction': '',
            'methodology': '',
            'results': '',
            'discussion': '',
            'conclusion': '',
            'references': '',
            'other': ''
        }
        
        # Convert to lowercase for pattern matching
        text_lower = full_text.lower()
        
        # Find section boundaries
        section_positions = {}
        for section_name, pattern in self.section_patterns.items():
            match = re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
            if match:
                section_positions[section_name] = match.start()
        
        # Sort sections by position
        sorted_sections = sorted(section_positions.items(), key=lambda x: x[1])
        
        # Extract text between sections
        for i, (section_name, start_pos) in enumerate(sorted_sections):
            end_pos = sorted_sections[i+1][1] if i+1 < len(sorted_sections) else len(full_text)
            sections[section_name] = full_text[start_pos:end_pos].strip()
        
        # Extract text before first section as "other"
        first_section_pos = min(section_positions.values()) if section_positions else 0
        if first_section_pos > 0:
            sections['other'] = full_text[:first_section_pos].strip()
        
        return sections
    
    def clean_text(self, text):
        """
        Clean and normalize extracted text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'\n\d+\s*\n', '\n', text)  # Page numbers
        text = re.sub(r'-\s*\n', '', text)  # Hyphenated line breaks
        
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def save_extracted_text(self, extracted_data, paper_title):
        """
        Save extracted text to JSON file
        """
        try:
            # Clean filename
            safe_title = re.sub(r'[^\w\s-]', '', paper_title)
            safe_title = re.sub(r'\s+', '_', safe_title)
            filename = f"{safe_title[:50]}_extracted.json"
            filepath = self.text_dir / filename
            
            # Save as JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Extracted text saved: {filename}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ Error saving extracted text: {e}")
            return None
    
    def process_all_papers(self, papers_metadata_file=None):
        """
        Process all PDFs in the papers directory
        """
        pdf_files = list(Config.PAPERS_DIR.glob("*.pdf"))
        
        if not pdf_files:
            print("❌ No PDF files found in papers directory")
            return []
        
        print(f"\n{'='*60}")
        print(f"📚 PROCESSING {len(pdf_files)} PAPERS")
        print(f"{'='*60}")
        
        all_extracted = []
        
        for pdf_file in pdf_files:
            # Extract text
            extracted = self.extract_text(pdf_file)
            
            if extracted:
                # Segment into sections
                sections = self.segment_into_sections(extracted)
                extracted['sections'] = sections
                
                # Clean text
                for page in extracted['pages']:
                    page['text'] = self.clean_text(page['text'])
                
                # Save to file
                saved_path = self.save_extracted_text(extracted, pdf_file.stem)
                extracted['saved_path'] = saved_path
                
                all_extracted.append(extracted)
        
        # Save master extraction log
        if all_extracted:
            master_file = self.text_dir / "all_extracted_papers.json"
            with open(master_file, 'w', encoding='utf-8') as f:
                json.dump(all_extracted, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Master extraction log saved: {master_file.name}")
        
        return all_extracted


def main():
    """Test the text extractor"""
    print("\n" + "="*60)
    print("           TEXT EXTRACTION MODULE")
    print("           Milestone 2: Part 1")
    print("="*60)
    
    extractor = TextExtractor()
    
    # Check for PDFs
    pdf_files = list(Config.PAPERS_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDFs found. Run paper_search.py first.")
        print("\n📝 To test with a sample PDF:")
        print("   1. Download a research paper PDF")
        print("   2. Place it in data/papers/ folder")
        print("   3. Run this script again")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF file(s)")
    
    # Process all papers or just one
    choice = input("\n🔧 Process all papers? (y/n): ").lower().strip()
    
    if choice == 'y':
        extractor.process_all_papers()
    else:
        # Process first paper only
        print(f"\n📄 Processing first paper: {pdf_files[0].name}")
        extracted = extractor.extract_text(pdf_files[0])
        
        if extracted:
            sections = extractor.segment_into_sections(extracted)
            print(f"\n📑 Sections found: {list(sections.keys())}")
            
            # Show sample from each section
            for section, text in sections.items():
                if text and len(text) > 50:
                    print(f"\n{section.upper()}:")
                    print(f"{text[:200]}..." if len(text) > 200 else text)
    
    print("\n" + "="*60)
    print("✅ Text extraction complete!")
    print(f"📁 Extracted texts saved in: {extractor.text_dir}")
    print("="*60)


if __name__ == "__main__":
    main()