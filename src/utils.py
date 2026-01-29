"""
utils.py - Utility functions for the Research Paper Reviewer
"""

import os
import re
import json
import requests
from datetime import datetime
from pathlib import Path
import time

try:
    from src.config import Config
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import Config


def create_filename(title):
    """Create a safe filename from title"""
    if not title:
        return f"paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Clean the title
    clean = re.sub(r'[^\w\s-]', '', str(title))
    clean = re.sub(r'\s+', '_', clean)
    clean = clean.strip('_')
    
    # Shorten if too long
    if len(clean) > 50:
        clean = clean[:50]
    
    # Add date
    timestamp = datetime.now().strftime("%Y%m%d")
    return f"{clean}_{timestamp}.pdf"


def download_pdf_file(pdf_url, save_path):
    """
    Download a PDF file with improved error handling and retries
    Returns: (success, file_size, error_message)
    """
    max_retries = 2
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            if not pdf_url or not isinstance(pdf_url, str):
                return False, 0, "Invalid URL"
            
            if attempt > 0:
                print(f"    🔄 Retry attempt {attempt + 1}...")
                time.sleep(retry_delay * attempt)
            
            # Enhanced headers to mimic browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }
            
            # Add referer on retry
            if attempt == 1:
                headers['Referer'] = 'https://www.semanticscholar.org/'
            
            print(f"    📥 Downloading from: {pdf_url[:80]}...")
            
            # Download with timeout
            response = requests.get(
                pdf_url, 
                headers=headers, 
                timeout=Config.DOWNLOAD_TIMEOUT, 
                stream=True,
                allow_redirects=True
            )
            
            # Check response
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}"
                if response.status_code == 403:
                    error_msg += " (Forbidden - may need different approach)"
                elif response.status_code == 404:
                    error_msg += " (Not Found)"
                elif response.status_code == 429:
                    error_msg += " (Rate Limited)"
                
                print(f"    ⚠️ {error_msg}")
                
                if response.status_code == 429 and attempt < max_retries - 1:
                    continue  # Retry on rate limit
                return False, 0, error_msg
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            content_length = response.headers.get('content-length')
            
            # Validate it's a PDF
            is_pdf = False
            if 'pdf' in content_type:
                is_pdf = True
            elif 'application/octet-stream' in content_type:
                # Could be PDF, check first bytes
                first_bytes = response.content[:5] if len(response.content) >= 5 else b''
                if first_bytes == b'%PDF-':
                    is_pdf = True
            
            if not is_pdf:
                # Check if it's HTML (redirect page)
                if 'text/html' in content_type:
                    return False, 0, "URL redirects to HTML page (not direct PDF)"
                return False, 0, f"Not a PDF file: {content_type}"
            
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
            if save_path.exists() and save_path.stat().st_size > 1024:  # At least 1KB
                file_size = save_path.stat().st_size
                
                # Double check it's a PDF
                with open(save_path, 'rb') as f:
                    first_bytes = f.read(5)
                    if first_bytes == b'%PDF-':
                        print(f"    ✅ Downloaded {file_size:,} bytes (verified PDF)")
                        return True, file_size, "Success"
                    else:
                        save_path.unlink()
                        return False, 0, "File is not a valid PDF"
            else:
                if save_path.exists():
                    save_path.unlink()
                return False, 0, "File too small or empty"
                
        except requests.exceptions.Timeout:
            print(f"    ⏰ Timeout (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                continue
            return False, 0, "Timeout"
            
        except requests.exceptions.ConnectionError:
            print(f"    🔌 Connection error (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                continue
            return False, 0, "Connection error"
            
        except requests.exceptions.TooManyRedirects:
            return False, 0, "Too many redirects"
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)[:100]}")
            if attempt < max_retries - 1:
                continue
            return False, 0, str(e)
    
    return False, 0, "All download attempts failed"


def save_metadata(papers):
    """Save paper metadata to JSON file"""
    try:
        metadata_file = Config.METADATA_DIR / "papers_metadata.json"
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Metadata saved: {metadata_file.name}")
        return True, str(metadata_file)
        
    except Exception as e:
        print(f"❌ Error saving metadata: {e}")
        return False, str(e)


def print_paper_details(paper, index):
    """Print formatted paper information"""
    print(f"\n{'='*60}")
    print(f"📄 PAPER {index}")
    print(f"{'='*60}")
    
    # Title
    title = paper.get('title', 'Unknown Title')
    if len(title) > 70:
        title = title[:70] + "..."
    print(f"📝 Title: {title}")
    
    # Authors
    authors = paper.get('authors', [])
    if authors:
        authors_str = ', '.join(authors[:3])
        if len(authors) > 3:
            authors_str += f" and {len(authors) - 3} more"
        print(f"👥 Authors: {authors_str}")
    
    # Year and citations
    year = paper.get('year', 'Unknown')
    citations = paper.get('citation_count', 0)
    print(f"📅 Year: {year} | 📈 Citations: {citations}")
    
    # Venue
    venue = paper.get('venue', '')
    if venue:
        print(f"🏛️  Venue: {venue[:50]}")
    
    # Abstract preview
    abstract = paper.get('abstract', '')
    if abstract and len(abstract) > 10:
        print(f"\n📋 Abstract Preview:")
        print(f"   {abstract[:150]}..." if len(abstract) > 150 else f"   {abstract}")
    
    # PDF status
    if paper.get('pdf_downloaded'):
        print(f"\n📄 PDF Status: ✅ Downloaded")
        if paper.get('file_path'):
            file_path = Path(paper['file_path'])
            if file_path.exists():
                size = file_path.stat().st_size
                if size > 1024 * 1024:
                    size_str = f"{size/(1024*1024):.2f} MB"
                else:
                    size_str = f"{size/1024:.1f} KB"
                print(f"   📏 Size: {size_str}")
                print(f"   📍 Location: {file_path.name}")
    else:
        print(f"\n📄 PDF Status: ❌ Not downloaded")
        error = paper.get('download_error', 'Unknown error')
        print(f"   ⚠️  Reason: {error}")
    
    print(f"{'='*60}")


def clean_text_for_display(text, max_length=200):
    """Clean and truncate text for display"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text


def format_file_size(bytes_size):
    """Format file size in human-readable format"""
    if bytes_size < 1024:
        return f"{bytes_size} bytes"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size/1024:.1f} KB"
    else:
        return f"{bytes_size/(1024*1024):.2f} MB"


if __name__ == "__main__":
    print("✅ Utils module loaded successfully")
    print(f"Download timeout: {Config.DOWNLOAD_TIMEOUT} seconds")