import os
import re
import json
import requests
from datetime import datetime
from pathlib import Path

try:
    from config import Config
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.config import Config

def create_filename(title):
    """Create a safe filename from title"""
    if not title:
        return f"paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Clean the title
    clean = re.sub(r'[^\w\s-]', '', str(title))
    clean = re.sub(r'\s+', '_', clean)
    
    # Shorten if too long
    if len(clean) > 50:
        clean = clean[:50]
    
    # Add date
    timestamp = datetime.now().strftime("%Y%m%d")
    return f"{clean}_{timestamp}.pdf"

def download_pdf_file(pdf_url, save_path):
    """
    Download a PDF file
    Returns: (success, file_size, error_message)
    """
    try:
        if not pdf_url or not isinstance(pdf_url, str):
            return False, 0, "Invalid URL"
        
        print(f"    📥 Downloading from: {pdf_url[:80]}...")
        
        # Headers
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/pdf'
        }
        
        # Download with timeout
        response = requests.get(pdf_url, headers=headers, timeout=30, stream=True)
        
        if response.status_code != 200:
            return False, 0, f"HTTP {response.status_code}"
        
        # Save file
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        total_size = 0
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    total_size += len(chunk)
        
        # Verify file
        if save_path.exists() and save_path.stat().st_size > 1000:
            file_size = save_path.stat().st_size
            return True, file_size, "Success"
        else:
            if save_path.exists():
                save_path.unlink()
            return False, 0, "File too small or empty"
            
    except requests.exceptions.Timeout:
        return False, 0, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, 0, "Connection error"
    except Exception as e:
        return False, 0, str(e)

def save_metadata(papers):
    """Save paper metadata"""
    try:
        metadata_file = Config.METADATA_DIR / "papers_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
        return True, str(metadata_file)
    except Exception as e:
        return False, str(e)

def print_paper_details(paper, index):
    """Print paper information"""
    print(f"\n{'='*60}")
    print(f"📄 PAPER {index}")
    print(f"{'='*60}")
    
    title = paper.get('title', 'Unknown Title')
    if len(title) > 70:
        title = title[:70] + "..."
    print(f"Title: {title}")
    
    print(f"Year: {paper.get('year', 'Unknown')}")
    print(f"Citations: {paper.get('citation_count', 0)}")
    
    # PDF status
    if paper.get('pdf_downloaded'):
        print(f"📄 PDF: ✅ Downloaded")
        if paper.get('file_path'):
            file_path = Path(paper['file_path'])
            if file_path.exists():
                size = file_path.stat().st_size
                size_str = f"{size/1024:.1f} KB" if size < 1024*1024 else f"{size/(1024*1024):.2f} MB"
                print(f"     Size: {size_str}")
    else:
        print(f"📄 PDF: ❌ Not downloaded")
    
    print(f"{'='*60}")

if __name__ == "__main__":
    print("✅ Utils module loaded")