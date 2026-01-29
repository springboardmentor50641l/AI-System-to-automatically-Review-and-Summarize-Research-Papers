import os
import sys
import requests
import json
from datetime import datetime
from pathlib import Path
import time

# Fix import paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.config import Config, get_api_headers
    from src.utils import create_filename, download_pdf_file, save_metadata, print_paper_details
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Trying alternative import approach...")
    
    # Try absolute import
    import sys
    sys.path.insert(0, os.path.dirname(project_root))
    
    try:
        from research_paper_reviewer.src.config import Config, get_api_headers
        from research_paper_reviewer.src.utils import create_filename, download_pdf_file, save_metadata, print_paper_details
    except ImportError:
        print("❌ Cannot import required modules")
        print("Please check your project structure")
        sys.exit(1)


class PaperSearchSystem:
    """Main system class for searching and downloading papers"""
    
    def __init__(self):
        """Initialize the system"""
        self.setup_complete = Config.setup_directories()
        self.session = requests.Session()
        
    def search_papers(self, topic):
        """
        Search for papers on Semantic Scholar
        Returns: list of papers with PDF URLs
        """
        print(f"\n🔍 Searching for: '{topic}'")
        
        # Validate API key
        if not Config.SEMANTIC_SCHOLAR_API_KEY:
            print("⚠️  No Semantic Scholar API key found")
            print("   You can still search, but rate limits apply")
        
        try:
            # Prepare request
            url = f"{Config.API_BASE_URL}/paper/search"
            params = {
                'query': topic,
                'limit': 20,  # Get more to find PDFs
                'offset': 0,
                'fields': 'title,year,abstract,citationCount,openAccessPdf,authors,paperId,url,venue,publicationTypes'
            }
            
            headers = get_api_headers()
            
            print("🌐 Contacting Semantic Scholar API...")
            response = self.session.get(url, params=params, headers=headers, timeout=Config.TIMEOUT)
            
            # Check response
            if response.status_code != 200:
                print(f"❌ API Error: {response.status_code}")
                if response.status_code == 429:
                    print("   ⏰ Rate limit exceeded. Please wait a few minutes.")
                    print("   💡 Get a free API key from: https://www.semanticscholar.org/product/api")
                elif response.status_code == 401:
                    print("   🔑 Invalid API key. Check your .env file.")
                elif response.status_code == 400:
                    print("   📝 Bad request. The topic might be too specific.")
                return []
            
            # Parse response
            data = response.json()
            all_papers = data.get('data', [])
            total_found = data.get('total', 0)
            
            if not all_papers:
                print("❌ No papers found for this topic")
                return []
            
            print(f"✅ Found {total_found} total papers")
            print(f"📄 Processing {len(all_papers)} papers from API...")
            
            # Process papers to find those with PDFs
            papers_with_pdfs = []
            papers_skipped_no_pdf = 0
            papers_skipped_other = 0
            
            for i, paper in enumerate(all_papers, 1):
                try:
                    # Get paper ID
                    paper_id = paper.get('paperId', '')
                    
                    # Get title - ensure it's a string
                    title = str(paper.get('title', 'No Title')).strip()
                    if not title or title == 'No Title':
                        papers_skipped_other += 1
                        continue
                    
                    # Skip papers older than 1990 (usually less relevant)
                    year = paper.get('year')
                    if year and int(year) < 1990:
                        continue
                    
                    # Get authors
                    authors_list = []
                    authors_data = paper.get('authors', [])
                    if isinstance(authors_data, list):
                        for author in authors_data[:4]:  # First 4 authors
                            if isinstance(author, dict):
                                author_name = author.get('name', '')
                                if author_name:
                                    authors_list.append(author_name)
                    
                    # Check for PDF - multiple approaches
                    pdf_url = None
                    
                    # Approach 1: Check openAccessPdf
                    open_access = paper.get('openAccessPdf')
                    if isinstance(open_access, dict):
                        pdf_url = open_access.get('url')
                    
                    # Approach 2: Check if URL ends with .pdf
                    paper_url = paper.get('url', '')
                    if not pdf_url and paper_url and paper_url.lower().endswith('.pdf'):
                        pdf_url = paper_url
                    
                    # Skip if no PDF
                    if not pdf_url or not isinstance(pdf_url, str) or not pdf_url.startswith('http'):
                        papers_skipped_no_pdf += 1
                        continue
                    
                    # Create paper object
                    paper_obj = {
                        'paper_id': paper_id,
                        'title': title,
                        'authors': authors_list,
                        'year': paper.get('year'),
                        'abstract': str(paper.get('abstract', '')[:300]),
                        'citation_count': paper.get('citationCount', 0),
                        'pdf_url': pdf_url,
                        'venue': paper.get('venue', ''),
                        'search_topic': topic,
                        'pdf_downloaded': False,
                        'file_name': None,
                        'file_path': None,
                        'download_date': None,
                        'publication_types': paper.get('publicationTypes', [])
                    }
                    
                    papers_with_pdfs.append(paper_obj)
                    
                    # Show progress for first few papers
                    if len(papers_with_pdfs) <= 3:
                        title_display = title[:60] + "..." if len(title) > 60 else title
                        print(f"  {len(papers_with_pdfs)}. {title_display}")
                    
                    # Stop if we have enough papers
                    if len(papers_with_pdfs) >= 10:  # Collect more than needed
                        break
                        
                except Exception as e:
                    papers_skipped_other += 1
                    continue
            
            print(f"\n📊 Search Summary:")
            print(f"   ✅ Papers with PDFs: {len(papers_with_pdfs)}")
            print(f"   ⏭️  Skipped (no PDF): {papers_skipped_no_pdf}")
            print(f"   ⏭️  Skipped (other): {papers_skipped_other}")
            
            if not papers_with_pdfs:
                print("\n❌ No papers with downloadable PDFs found")
                print("\n💡 Suggestions:")
                print("   • Try a different topic")
                print("   • Some papers may not have open access PDFs")
                print("   • Try: 'machine learning', 'artificial intelligence', 'deep learning'")
                return []
            
            # Sort by citation count (higher is usually better quality)
            papers_with_pdfs.sort(key=lambda x: x.get('citation_count', 0), reverse=True)
            
            print(f"\n✅ Found {len(papers_with_pdfs)} papers with PDFs")
            return papers_with_pdfs[:Config.MAX_PAPERS_TO_DOWNLOAD]  # Return top N
            
        except requests.exceptions.Timeout:
            print("❌ Request timeout. Check your internet connection.")
            return []
        except requests.exceptions.ConnectionError:
            print("❌ Connection error. Check your internet.")
            return []
        except json.JSONDecodeError:
            print("❌ Error parsing API response.")
            return []
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)[:100]}")
            return []
    
    def download_papers(self, papers):
        """
        Download PDFs for papers
        Returns: list of downloaded papers
        """
        if not papers:
            print("❌ No papers to download")
            return []
        
        print(f"\n📥 Downloading {len(papers)} PDF file(s)...")
        
        downloaded_papers = []
        
        for i, paper in enumerate(papers, 1):
            pdf_url = paper.get('pdf_url')
            
            if not pdf_url:
                print(f"\n[{i}] ❌ No PDF URL")
                continue
            
            # Create filename
            filename = create_filename(paper['title'])
            filepath = str(Config.PAPERS_DIR / filename)
            
            print(f"\n[{i}] 📄 {filename}")
            print(f"    🔗 Source: {pdf_url[:80]}...")
            
            # Download the PDF
            success, file_size, error_msg = download_pdf_file(pdf_url, filepath)
            
            if success:
                paper['pdf_downloaded'] = True
                paper['file_name'] = filename
                paper['file_path'] = filepath
                paper['file_size'] = file_size
                paper['download_date'] = datetime.now().isoformat()
                downloaded_papers.append(paper)
                
                print(f"    ✅ Success! ({file_size:,} bytes)")
            else:
                paper['pdf_downloaded'] = False
                paper['download_error'] = error_msg
                print(f"    ❌ Failed: {error_msg}")
        
        print(f"\n📊 Download Summary:")
        print(f"   📤 Attempted: {len(papers)}")
        print(f"   ✅ Successful: {len(downloaded_papers)}")
        print(f"   ❌ Failed: {len(papers) - len(downloaded_papers)}")
        
        return downloaded_papers
    
    def create_dataset(self, papers):
        """Create and save complete dataset"""
        if not papers:
            print("❌ No data to save")
            return False
        
        try:
            dataset = {
                'project': 'AI Research Paper Reviewer',
                'milestone': 1,
                'created_at': datetime.now().isoformat(),
                'search_topic': papers[0].get('search_topic', 'Unknown') if papers else 'Unknown',
                'total_papers_found': len(papers),
                'papers_downloaded': sum(1 for p in papers if p.get('pdf_downloaded')),
                'papers': papers,
                'data_location': str(Config.DATA_DIR),
                'system_version': '1.0.0'
            }
            
            # Save dataset
            dataset_file = Config.DATASET_FILE
            dataset_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(dataset_file, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Dataset saved to: {dataset_file.name}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving dataset: {e}")
            return False
    
    def check_results(self):
        """Check what files were downloaded"""
        print(f"\n📁 Checking results in: {Config.PAPERS_DIR}")
        
        if not Config.PAPERS_DIR.exists():
            print("❌ Papers directory not found")
            return 0
        
        pdf_files = list(Config.PAPERS_DIR.glob("*.pdf"))
        
        if not pdf_files:
            print("❌ No PDF files downloaded")
            return 0
        
        print(f"✅ Found {len(pdf_files)} PDF file(s):")
        for pdf in pdf_files:
            size = pdf.stat().st_size
            if size > 1024 * 1024:  # More than 1MB
                size_str = f"{size/(1024*1024):.2f} MB"
            else:
                size_str = f"{size/1024:.1f} KB"
            print(f"  • {pdf.name} ({size_str})")
        
        return len(pdf_files)
    
    def get_suggested_topics(self):
        """Get suggested research topics"""
        return [
            "machine learning",
            "artificial intelligence",
            "deep learning",
            "natural language processing",
            "computer vision",
            "reinforcement learning",
            "neural networks",
            "data science",
            "big data",
            "internet of things"
        ]


def main():
    """Main function - runs everything for Milestone 1"""
    print("\n" + "="*60)
    print("           AI RESEARCH PAPER COLLECTOR")
    print("           Milestone 1: Paper Search & Download")
    print("="*60)
    
    # Initialize system
    print("\n🚀 Initializing system...")
    system = PaperSearchSystem()
    
    if not system.setup_complete:
        print("❌ Failed to setup directories")
        return
    
    # Show suggested topics
    print("\n💡 Suggested topics:")
    suggested = system.get_suggested_topics()
    for i, topic in enumerate(suggested[:5], 1):
        print(f"   {i}. {topic}")
    
    # Get search topic
    topic = input("\n🔎 Enter research topic: ").strip()
    
    if not topic:
        print("❌ Please enter a topic")
        print("\n📝 Example: machine learning in healthcare")
        return
    
    # Remove quotes if user entered them
    topic = topic.strip("'\"")
    
    print("\n" + "="*60)
    print(f"STEP 1: SEARCHING FOR PAPERS")
    print("="*60)
    
    # Search for papers
    papers = system.search_papers(topic)
    
    if not papers:
        print("\n❌ No papers found. Try a different topic.")
        return
    
    print("\n" + "="*60)
    print("STEP 2: DOWNLOADING PDFS")
    print("="*60)
    
    # Download papers
    downloaded_papers = system.download_papers(papers)
    
    if not downloaded_papers:
        print("\n❌ No PDFs were downloaded.")
        print("\n🔧 Possible reasons:")
        print("   1. PDF links are broken or require authentication")
        print("   2. Network or firewall issues")
        print("   3. Server timeout")
        print("   4. Papers don't have open access PDFs")
        print("\n💡 Try:")
        print("   • Different research topic")
        print("   • Check internet connection")
        print("   • Use VPN if in restricted network")
        return
    
    print("\n" + "="*60)
    print("STEP 3: SAVING DATA")
    print("="*60)
    
    # Save metadata
    metadata_success, metadata_msg = save_metadata(downloaded_papers)
    if metadata_success:
        print(f"✅ Metadata saved")
    else:
        print(f"❌ Metadata error: {metadata_msg}")
    
    # Save dataset
    dataset_success = system.create_dataset(downloaded_papers)
    
    print("\n" + "="*60)
    print("STEP 4: RESULTS SUMMARY")
    print("="*60)
    
    # Show paper details
    print(f"\n📄 Downloaded Papers:")
    for i, paper in enumerate(downloaded_papers, 1):
        print_paper_details(paper, i)
    
    # Check files
    pdf_count = system.check_results()
    
    print("\n" + "="*60)
    
    if pdf_count >= 1:
        print("🎯 MILESTONE 1 COMPLETE!")
        print(f"\n✅ Successfully downloaded {pdf_count} PDF file(s)")
        print(f"📁 Data location: {Config.DATA_DIR}")
        print(f"📄 PDFs: {Config.PAPERS_DIR}")
        print(f"📋 Metadata: {Config.METADATA_DIR}")
        print(f"📊 Dataset: {Config.DATASET_FILE}")
        
        print("\n📋 Next Steps (Milestone 2):")
        print("   1. Extract text from downloaded PDFs")
        print("   2. Clean and preprocess the text")
        print("   3. Prepare for analysis")
        print("\n💡 Run: python -m src.text_extraction")
    else:
        print("⚠️  Partial Completion")
        print("   Some PDFs failed to download")
        print("   Check the error messages above")
    
    print("\n" + "="*60)


# Run the program
if __name__ == "__main__":
    main()