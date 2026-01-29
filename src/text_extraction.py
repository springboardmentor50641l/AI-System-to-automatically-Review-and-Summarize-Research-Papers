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
import sys

warnings.filterwarnings('ignore')

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.config import Config
    from src.utils import create_filename
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Trying alternative import...")
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.config import Config
    from src.utils import create_filename


class TextExtractor:
    """Extract text from PDFs with multiple fallback methods"""
    
    def __init__(self):
        """Initialize extractor with configuration"""
        self.text_dir = Config.EXTRACTED_TEXT_DIR
        self.text_dir.mkdir(exist_ok=True)
        
        # Download NLTK data if needed
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            print("📥 Downloading NLTK data...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        
        # Section patterns for academic papers (improved)
        self.section_patterns = {
            'title': r'^((?!abstract|introduction|method|result|discussion|conclusion|reference)[A-Z][A-Za-z\s]+)$',
            'abstract': r'^\s*(abstract|summary)\s*$',
            'introduction': r'^\s*(1\.?\s*)?introduction\s*$',
            'literature': r'^\s*(2\.?\s*)?(related work|literature review|background)\s*$',
            'methodology': r'^\s*(3\.?\s*)?(methodology|methods|materials and methods|experimental setup)\s*$',
            'results': r'^\s*(4\.?\s*)?(results|findings|experimental results)\s*$',
            'discussion': r'^\s*(5\.?\s*)?discussion\s*$',
            'conclusion': r'^\s*(6\.?\s*)?(conclusion|conclusions|summary and conclusions)\s*$',
            'references': r'^\s*(references|bibliography)\s*$'
        }
    
    def extract_with_pymupdf(self, pdf_path):
        """
        Extract text using PyMuPDF (fastest for text-based PDFs)
        Returns: List of pages with text and metadata
        """
        try:
            doc = fitz.open(pdf_path)
            pages_data = []
            
            total_pages = len(doc)
            print(f"📖 Extracting with PyMuPDF ({total_pages} pages)...")
            
            for page_num in tqdm(range(total_pages), desc="Pages", unit="page"):
                page = doc.load_page(page_num)
                
                # Extract text with better formatting
                text = page.get_text("text")
                
                # Extract metadata
                page_rect = page.rect
                images = page.get_images()
                
                pages_data.append({
                    'page_number': page_num + 1,
                    'text': text.strip(),
                    'method': 'pymupdf',
                    'page_width': page_rect.width,
                    'page_height': page_rect.height,
                    'has_images': len(images) > 0,
                    'image_count': len(images)
                })
            
            doc.close()
            return pages_data
            
        except Exception as e:
            print(f"❌ PyMuPDF extraction failed: {e}")
            return []
    
    def extract_with_pdfplumber(self, pdf_path):
        """
        Extract text using pdfplumber (better for complex layouts and tables)
        """
        try:
            pages_data = []
            
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                print(f"📖 Extracting with pdfplumber ({total_pages} pages)...")
                
                for page_num, page in enumerate(tqdm(pdf.pages, desc="Pages", unit="page"), 1):
                    # Extract text
                    text = page.extract_text() or ""
                    
                    # Extract tables if any
                    tables_text = ""
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            for row in table:
                                row_text = " | ".join([str(cell) if cell else "" for cell in row])
                                tables_text += row_text + "\n"
                    
                    # Extract page dimensions
                    width = page.width
                    height = page.height
                    
                    pages_data.append({
                        'page_number': page_num,
                        'text': text.strip(),
                        'tables': tables_text.strip(),
                        'method': 'pdfplumber',
                        'page_width': width,
                        'page_height': height,
                        'has_tables': len(tables) > 0
                    })
            
            return pages_data
            
        except Exception as e:
            print(f"❌ PDFPlumber extraction failed: {e}")
            return []
    
    def extract_with_ocr(self, pdf_path):
        """
        Extract text using OCR (for scanned PDFs)
        Note: Requires Tesseract OCR installed on system
        """
        try:
            # Check if tesseract is available
            pytesseract.get_tesseract_version()
            
            doc = fitz.open(pdf_path)
            pages_data = []
            
            total_pages = len(doc)
            print(f"🔍 Using OCR for scanned PDF ({total_pages} pages)...")
            
            for page_num in tqdm(range(total_pages), desc="OCR Pages", unit="page"):
                page = doc.load_page(page_num)
                
                # Get image of page with higher DPI for better OCR
                zoom = 2  # Zoom factor for better resolution
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("ppm")
                image = Image.open(io.BytesIO(img_data))
                
                # Perform OCR
                try:
                    text = pytesseract.image_to_string(image)
                except:
                    # Fallback to basic OCR
                    text = ""
                
                pages_data.append({
                    'page_number': page_num + 1,
                    'text': text.strip(),
                    'method': 'ocr',
                    'resolution': f"{pix.width}x{pix.height}",
                    'zoom_factor': zoom
                })
            
            doc.close()
            return pages_data
            
        except Exception as e:
            print(f"❌ OCR extraction failed: {e}")
            print("💡 Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
            return []
    
    def detect_pdf_type(self, pdf_path):
        """Detect if PDF is text-based or scanned"""
        try:
            doc = fitz.open(pdf_path)
            text_content = ""
            
            # Sample first few pages
            for page_num in range(min(3, len(doc))):
                page = doc.load_page(page_num)
                text_content += page.get_text()
            
            doc.close()
            
            # If we get reasonable amount of text, it's text-based
            if len(text_content) > 500:
                return "text_based"
            else:
                return "scanned"
                
        except:
            return "unknown"
    
    def extract_text(self, pdf_path):
        """
        Main extraction method with intelligent fallback strategies
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            print(f"❌ PDF not found: {pdf_path}")
            return None
        
        print(f"\n{'='*60}")
        print(f"📄 Processing: {pdf_path.name}")
        print(f"{'='*60}")
        
        # Detect PDF type
        pdf_type = self.detect_pdf_type(pdf_path)
        print(f"📊 PDF Type: {pdf_type}")
        
        # Try extraction based on detected type
        if pdf_type == "text_based":
            # Try PyMuPDF first (fastest)
            pages_data = self.extract_with_pymupdf(pdf_path)
            
            # If little text extracted, try pdfplumber
            total_text = sum(len(page['text']) for page in pages_data)
            if total_text < 1000 and len(pages_data) > 0:
                print("⚠️  Low text count, trying pdfplumber...")
                alt_data = self.extract_with_pdfplumber(pdf_path)
                
                # Use whichever extracted more text
                alt_text = sum(len(page['text']) for page in alt_data)
                if alt_text > total_text * 1.5:  # 50% more text
                    pages_data = alt_data
                    print(f"✅ Switched to pdfplumber (got {alt_text:,} chars)")
        
        else:  # Scanned or unknown
            print("🖨️  PDF appears to be scanned, trying OCR...")
            pages_data = self.extract_with_ocr(pdf_path)
            
            # Fallback to basic extraction if OCR fails
            total_text = sum(len(page['text']) for page in pages_data)
            if total_text < 500:
                print("⚠️  OCR extracted little text, trying regular extraction...")
                fallback_data = self.extract_with_pymupdf(pdf_path)
                fallback_text = sum(len(page['text']) for page in fallback_data)
                
                if fallback_text > total_text:
                    pages_data = fallback_data
        
        # Check if extraction was successful
        if not pages_data:
            print("❌ All extraction methods failed")
            return None
        
        # Calculate statistics
        total_pages = len(pages_data)
        total_chars = sum(len(page['text']) for page in pages_data)
        total_words = sum(len(page['text'].split()) for page in pages_data)
        extraction_method = pages_data[0]['method'] if pages_data else 'failed'
        
        print(f"\n📊 Extraction Statistics:")
        print(f"   📑 Pages: {total_pages}")
        print(f"   🔤 Characters: {total_chars:,}")
        print(f"   📝 Words: {total_words:,}")
        print(f"   ⚙️  Method: {extraction_method}")
        
        if total_words < 100:
            print("⚠️  Warning: Very little text extracted")
        
        return {
            'file_name': pdf_path.name,
            'file_path': str(pdf_path),
            'file_size': pdf_path.stat().st_size,
            'extraction_date': datetime.now().isoformat(),
            'pdf_type': pdf_type,
            'total_pages': total_pages,
            'total_chars': total_chars,
            'total_words': total_words,
            'extraction_method': extraction_method,
            'pages': pages_data
        }
    
    def segment_into_sections(self, extracted_data):
        """
        Identify and segment paper into standard sections using rule-based approach
        """
        if not extracted_data or 'pages' not in extracted_data:
            return {}
        
        # Combine all pages text
        full_text = "\n\n".join([page['text'] for page in extracted_data['pages']])
        
        # Default sections
        sections = {
            'title': '',
            'abstract': '',
            'introduction': '',
            'literature_review': '',
            'methodology': '',
            'results': '',
            'discussion': '',
            'conclusion': '',
            'references': '',
            'other': ''
        }
        
        # Convert to lowercase for pattern matching
        text_lower = full_text.lower()
        lines = full_text.split('\n')
        
        # Find potential section headers
        section_positions = {}
        
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            
            # Check each pattern
            for section_name, pattern in self.section_patterns.items():
                if re.search(pattern, line_lower, re.IGNORECASE):
                    # Store position and original line
                    section_positions[section_name] = {
                        'position': i,
                        'original_line': line.strip()
                    }
                    break
        
        # If no sections found, use heuristics
        if not section_positions:
            print("⚠️  No section headers found, using paragraph-based segmentation")
            paragraphs = [p.strip() for p in full_text.split('\n\n') if p.strip()]
            
            if paragraphs:
                # First paragraph might be title/abstract
                if len(paragraphs[0]) < 200 and len(paragraphs[0].split()) < 20:
                    sections['title'] = paragraphs[0]
                
                # Next few paragraphs
                if len(paragraphs) > 1:
                    sections['abstract'] = paragraphs[1]
                
                # Distribute remaining paragraphs
                remaining = paragraphs[2:] if len(paragraphs) > 2 else paragraphs[1:]
                chunk_size = len(remaining) // 4
                
                if chunk_size > 0:
                    sections['introduction'] = '\n\n'.join(remaining[:chunk_size])
                    sections['methodology'] = '\n\n'.join(remaining[chunk_size:chunk_size*2])
                    sections['results'] = '\n\n'.join(remaining[chunk_size*2:chunk_size*3])
                    sections['conclusion'] = '\n\n'.join(remaining[chunk_size*3:])
            
            return sections
        
        # Sort sections by position
        sorted_sections = sorted(section_positions.items(), key=lambda x: x[1]['position'])
        
        # Extract text between sections
        for i, (section_name, info) in enumerate(sorted_sections):
            start_pos = info['position']
            start_line = lines[start_pos]
            
            # Find end position (next section or end)
            if i + 1 < len(sorted_sections):
                end_pos = sorted_sections[i + 1][1]['position']
            else:
                end_pos = len(lines)
            
            # Extract lines for this section (excluding the header line itself)
            section_lines = lines[start_pos + 1:end_pos]
            section_text = '\n'.join(section_lines).strip()
            
            sections[section_name] = section_text
        
        # Extract text before first section
        first_section_pos = min([info['position'] for info in section_positions.values()])
        if first_section_pos > 0:
            preamble = '\n'.join(lines[:first_section_pos]).strip()
            if preamble:
                # Try to identify if it's title/abstract
                if len(preamble) < 300 and 'abstract' not in preamble.lower():
                    if not sections['title']:
                        sections['title'] = preamble
                    else:
                        sections['abstract'] = preamble
                else:
                    sections['other'] = preamble
        
        return sections
    
    def clean_text(self, text):
        """
        Clean and normalize extracted text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace but preserve paragraph breaks
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Fix hyphenated words across lines
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        # Remove page numbers and headers/footers (common patterns)
        text = re.sub(r'\n\d+\s*\n', '\n', text)  # Page numbers on their own line
        text = re.sub(r'^[A-Z][A-Z\s]+\n', '', text, flags=re.MULTILINE)  # ALL CAPS headers
        
        # Remove URLs and emails
        text = re.sub(r'http\S+|www\.\S+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove common artifacts
        text = re.sub(r'�', '', text)  # Replacement character
        text = re.sub(r'\x0c', '', text)  # Form feed
        
        # Normalize quotes and dashes
        text = text.replace('``', '"').replace("''", '"')
        text = text.replace('–', '-').replace('—', '-')
        
        return text.strip()
    
    def save_extracted_text(self, extracted_data, paper_title):
        """
        Save extracted text to JSON file
        """
        try:
            # Clean filename
            safe_title = re.sub(r'[^\w\s-]', '', paper_title)
            safe_title = re.sub(r'\s+', '_', safe_title)
            safe_title = safe_title.strip('_')
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
    
    def process_all_papers(self):
        """
        Process all PDFs in the papers directory
        """
        pdf_files = list(Config.PAPERS_DIR.glob("*.pdf"))
        
        if not pdf_files:
            print("❌ No PDF files found in papers directory")
            print(f"📁 Directory: {Config.PAPERS_DIR}")
            return []
        
        print(f"\n{'='*60}")
        print(f"📚 PROCESSING {len(pdf_files)} PAPERS")
        print(f"{'='*60}")
        
        all_extracted = []
        
        for pdf_file in pdf_files:
            try:
                # Extract text
                extracted = self.extract_text(pdf_file)
                
                if extracted:
                    # Clean text in pages
                    for page in extracted['pages']:
                        page['text'] = self.clean_text(page['text'])
                    
                    # Segment into sections
                    sections = self.segment_into_sections(extracted)
                    extracted['sections'] = sections
                    
                    # Save to file
                    saved_path = self.save_extracted_text(extracted, pdf_file.stem)
                    extracted['saved_path'] = saved_path
                    
                    all_extracted.append(extracted)
                    
                    print(f"✅ Completed: {pdf_file.name}")
                else:
                    print(f"❌ Failed to extract: {pdf_file.name}")
                    
            except Exception as e:
                print(f"❌ Error processing {pdf_file.name}: {e}")
        
        # Save master extraction log
        if all_extracted:
            master_file = self.text_dir / "all_extracted_papers.json"
            try:
                with open(master_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'total_papers': len(all_extracted),
                        'extraction_date': datetime.now().isoformat(),
                        'papers': all_extracted
                    }, f, indent=2, ensure_ascii=False)
                print(f"\n✅ Master extraction log saved: {master_file.name}")
            except Exception as e:
                print(f"❌ Error saving master log: {e}")
        
        print(f"\n📊 Extraction Summary:")
        print(f"   ✅ Successfully processed: {len(all_extracted)}/{len(pdf_files)}")
        
        return all_extracted


def main():
    """Main entry point for text extraction"""
    print("\n" + "="*60)
    print("           TEXT EXTRACTION MODULE")
    print("           Milestone 2: Part 1")
    print("="*60)
    
    # Setup directories
    Config.setup_directories()
    
    extractor = TextExtractor()
    
    # Check for PDFs
    pdf_files = list(Config.PAPERS_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDFs found. Run Milestone 1 first.")
        print(f"\n📁 Expected directory: {Config.PAPERS_DIR}")
        print("\n📝 To test with a sample PDF:")
        print("   1. Download a research paper PDF")
        print("   2. Place it in: data/papers/")
        print("   3. Run this script again")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF file(s)")
    
    # Show available PDFs
    print("\n📚 Available PDFs:")
    for i, pdf_file in enumerate(pdf_files, 1):
        size = pdf_file.stat().st_size
        size_str = f"{size/1024:.1f} KB" if size < 1024*1024 else f"{size/(1024*1024):.2f} MB"
        print(f"  {i}. {pdf_file.name} ({size_str})")
    
    # Ask user what to process
    print("\n🔧 Processing options:")
    print("   A - Process all papers")
    print("   S - Process single paper")
    print("   T - Test extraction on first paper")
    
    choice = input("\n👉 Enter choice (A/S/T): ").upper().strip()
    
    if choice == 'A':
        # Process all papers
        extractor.process_all_papers()
        
    elif choice == 'S':
        # Let user choose which paper to process
        if len(pdf_files) > 1:
            try:
                paper_num = int(input(f"Enter paper number (1-{len(pdf_files)}): "))
                if 1 <= paper_num <= len(pdf_files):
                    selected_pdf = pdf_files[paper_num - 1]
                else:
                    print("❌ Invalid number, using first paper")
                    selected_pdf = pdf_files[0]
            except:
                print("❌ Invalid input, using first paper")
                selected_pdf = pdf_files[0]
        else:
            selected_pdf = pdf_files[0]
        
        print(f"\n📄 Processing: {selected_pdf.name}")
        extracted = extractor.extract_text(selected_pdf)
        
        if extracted:
            sections = extractor.segment_into_sections(extracted)
            
            print(f"\n📑 Sections identified:")
            for section, text in sections.items():
                if text and len(text.strip()) > 0:
                    word_count = len(text.split())
                    print(f"   • {section}: {word_count} words")
            
            # Show preview of each section
            print(f"\n📋 Section Previews:")
            for section, text in sections.items():
                if text and len(text.strip()) > 50:
                    preview = text[:150] + "..." if len(text) > 150 else text
                    print(f"\n{section.upper()}:")
                    print(f"{preview}")
            
            # Ask to save
            save = input("\n💾 Save extracted text? (y/n): ").lower().strip()
            if save == 'y':
                saved_path = extractor.save_extracted_text(extracted, selected_pdf.stem)
                if saved_path:
                    print(f"✅ Saved to: {saved_path}")
    
    elif choice == 'T':
        # Test extraction on first paper
        print(f"\n🧪 Testing extraction on: {pdf_files[0].name}")
        extracted = extractor.extract_text(pdf_files[0])
        
        if extracted:
            print(f"\n✅ Extraction successful!")
            print(f"📊 Pages: {extracted['total_pages']}")
            print(f"📝 Words: {extracted['total_words']}")
            print(f"⚙️  Method: {extracted['extraction_method']}")
            
            # Show sample text
            if extracted['pages'] and len(extracted['pages']) > 0:
                sample_text = extracted['pages'][0]['text'][:200]
                print(f"\n📋 Sample text (first 200 chars):")
                print(f"{sample_text}...")
        else:
            print("❌ Extraction failed")
    
    else:
        print("❌ Invalid choice")
    
    print("\n" + "="*60)
    print("✅ Text extraction module complete!")
    print(f"📁 Extracted texts saved in: {extractor.text_dir}")
    print("\n📋 Next Steps (Milestone 2 Part 2):")
    print("   • Run paper analyzer: python -m src.paper_analyzer")
    print("   • Or run complete pipeline: python -m src.pipeline")
    print("="*60)


if __name__ == "__main__":
    main()