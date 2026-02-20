#!/usr/bin/env python3
"""
Main Entry Point for Automated Research Review System
Provides CLI interface for running the complete pipeline or individual modules.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Import package modules
from automated_research_review import (
    __version__,
    PaperSearcher,
    TextExtractor,
    PaperAnalyzer,
    DraftGenerator,
    setup_logging,
    create_directories,
    check_environment,
    DATA_DIR,
    PAPERS_DIR,
    EXTRACTED_DIR,
    ANALYSIS_DIR,
    DRAFTS_DIR
)

# Setup logging
logger = setup_logging()

class ResearchReviewPipeline:
    """
    Main pipeline orchestrator for the research review system.
    Can run the complete workflow or individual stages.
    """
    
    def __init__(self, topic: str, max_papers: int = 3):
        """
        Initialize the pipeline.
        
        Args:
            topic: Research topic to process
            max_papers: Maximum number of papers to download
        """
        self.topic = topic
        self.max_papers = max_papers
        self.start_time = datetime.now()
        
        # Initialize modules
        self.searcher = PaperSearcher()
        self.extractor = TextExtractor()
        self.analyzer = PaperAnalyzer()
        self.generator = DraftGenerator()
        
        # Pipeline state
        self.state = {
            "topic": topic,
            "papers": [],
            "extracted_files": [],
            "analysis_files": [],
            "draft": None,
            "draft_path": None,
            "errors": []
        }
    
    def print_header(self, stage: str):
        """Print stage header."""
        print(f"\n{'='*60}")
        print(f"📋 Stage: {stage}")
        print(f"{'='*60}")
    
    def print_success(self, message: str):
        """Print success message."""
        print(f"✅ {message}")
    
    def print_error(self, message: str):
        """Print error message."""
        print(f"❌ {message}")
    
    def print_info(self, message: str):
        """Print info message."""
        print(f"ℹ️ {message}")
    
    def stage_1_search(self) -> bool:
        """
        Stage 1: Search and download papers.
        
        Returns:
            True if successful, False otherwise
        """
        self.print_header("1. Paper Search & Download")
        print(f"🔍 Searching for: '{self.topic}'")
        print(f"📊 Max papers: {self.max_papers}")
        
        try:
            result = self.searcher.process_topic(self.topic)
            
            if result["success"]:
                self.state["papers"] = result["papers"]
                self.print_success(result["message"])
                
                # List downloaded papers
                for i, paper in enumerate(result["papers"], 1):
                    print(f"   {i}. {paper['title']}")
                    print(f"      📍 {Path(paper['local_path']).name}")
                
                return True
            else:
                self.print_error(result["message"])
                self.state["errors"].append(f"Search failed: {result['message']}")
                return False
                
        except Exception as e:
            self.print_error(f"Search stage failed: {e}")
            self.state["errors"].append(str(e))
            return False
    
    def stage_2_extract(self) -> bool:
        """
        Stage 2: Extract text from PDFs.
        
        Returns:
            True if successful, False otherwise
        """
        self.print_header("2. Text Extraction")
        
        try:
            # Check if we have PDFs
            pdf_files = list(PAPERS_DIR.glob("*.pdf"))
            if not pdf_files:
                self.print_error("No PDF files found to extract")
                return False
            
            print(f"📄 Found {len(pdf_files)} PDFs to process")
            
            # Extract text
            saved_files = self.extractor.process_all_pdfs(PAPERS_DIR)
            
            if saved_files:
                self.state["extracted_files"] = saved_files
                self.print_success(f"Extracted text from {len(saved_files)} papers")
                
                # List extracted files
                for path in saved_files[:5]:
                    print(f"   📄 {Path(path).name}")
                
                return True
            else:
                self.print_error("No text extracted from any PDF")
                self.state["errors"].append("Extraction failed")
                return False
                
        except Exception as e:
            self.print_error(f"Extraction stage failed: {e}")
            self.state["errors"].append(str(e))
            return False
    
    def stage_3_analyze(self) -> bool:
        """
        Stage 3: Analyze extracted papers.
        
        Returns:
            True if successful, False otherwise
        """
        self.print_header("3. Paper Analysis")
        
        try:
            # Check if we have extracted text
            extracted_files = list(EXTRACTED_DIR.glob("*.json"))
            if not extracted_files:
                self.print_error("No extracted text files found")
                return False
            
            print(f"🔬 Found {len(extracted_files)} papers to analyze")
            print("   This may take a few minutes...")
            
            # Analyze papers
            analysis_paths = self.analyzer.process_all_papers(EXTRACTED_DIR)
            
            if analysis_paths:
                self.state["analysis_files"] = analysis_paths
                self.print_success(f"Analyzed {len(analysis_paths)} papers")
                
                # List analysis files
                for path in analysis_paths[:5]:
                    print(f"   🔬 {Path(path).name}")
                
                return True
            else:
                self.print_error("No papers successfully analyzed")
                self.state["errors"].append("Analysis failed")
                return False
                
        except Exception as e:
            self.print_error(f"Analysis stage failed: {e}")
            self.state["errors"].append(str(e))
            return False
    
    def stage_4_draft(self) -> bool:
        """
        Stage 4: Generate final draft.
        
        Returns:
            True if successful, False otherwise
        """
        self.print_header("4. Draft Generation")
        
        try:
            # Check if we have analysis files
            analysis_files = list(ANALYSIS_DIR.glob("*_analysis.json"))
            if not analysis_files:
                self.print_error("No analysis files found")
                return False
            
            print(f"✍️ Generating draft from {len(analysis_files)} papers...")
            
            # Generate draft
            result = self.generator.generate_review(self.topic)
            
            if result["success"]:
                self.state["draft"] = result["draft"]
                self.state["draft_path"] = result["draft_path"]
                self.print_success(result["message"])
                print(f"   📝 Draft saved: {result['draft_path']}")
                
                # Show preview
                print("\n📖 Draft Preview:")
                print("-" * 40)
                preview = result["draft"][:500] + "..." if len(result["draft"]) > 500 else result["draft"]
                print(preview)
                print("-" * 40)
                
                return True
            else:
                self.print_error(result["message"])
                self.state["errors"].append(f"Draft generation failed: {result['message']}")
                return False
                
        except Exception as e:
            self.print_error(f"Draft generation failed: {e}")
            self.state["errors"].append(str(e))
            return False
    
    def run_complete(self) -> Dict[str, Any]:
        """
        Run the complete pipeline from search to draft.
        
        Returns:
            Dictionary with pipeline results
        """
        print("\n" + "="*60)
        print(f"🚀 COMPLETE RESEARCH REVIEW PIPELINE")
        print(f"📚 Topic: {self.topic}")
        print("="*60 + "\n")
        
        # Run stages sequentially
        stages = [
            ("Search", self.stage_1_search),
            ("Extraction", self.stage_2_extract),
            ("Analysis", self.stage_3_analyze),
            ("Draft", self.stage_4_draft)
        ]
        
        for stage_name, stage_func in stages:
            if not stage_func():
                self.print_error(f"Pipeline stopped at {stage_name} stage")
                break
        
        # Calculate execution time
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 PIPELINE SUMMARY")
        print("="*60)
        print(f"Topic: {self.topic}")
        print(f"Status: {'✅ Complete' if not self.state['errors'] else '⚠️ Partial'}")
        print(f"Duration: {duration:.1f} seconds")
        print(f"Papers downloaded: {len(self.state['papers'])}")
        print(f"Papers extracted: {len(self.state['extracted_files'])}")
        print(f"Papers analyzed: {len(self.state['analysis_files'])}")
        
        if self.state['draft_path']:
            print(f"Draft saved: {self.state['draft_path']}")
        
        if self.state['errors']:
            print("\n❌ Errors encountered:")
            for error in self.state['errors']:
                print(f"   • {error}")
        
        print("="*60 + "\n")
        
        return self.state
    
    def get_summary(self) -> str:
        """Get a text summary of the pipeline results."""
        summary = []
        summary.append(f"Research Review: {self.topic}")
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")
        
        if self.state['papers']:
            summary.append(f"📚 Papers Analyzed ({len(self.state['papers'])}):")
            for paper in self.state['papers']:
                summary.append(f"   • {paper['title']}")
        
        if self.state['draft']:
            summary.append("")
            summary.append("📝 Draft Preview:")
            summary.append("-" * 40)
            summary.append(self.state['draft'][:1000])
        
        return "\n".join(summary)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Automated Research Review System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline
  python main.py run "machine learning transformers"
  
  # Run specific stage only
  python main.py search "graph neural networks"
  python main.py extract
  python main.py analyze
  python main.py draft "climate change"
  
  # List downloaded papers
  python main.py list papers
  
  # Check system status
  python main.py status
  
  # Clean data directories
  python main.py clean --dry-run
        """
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'Automated Research Review System v{__version__}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Run complete pipeline
    run_parser = subparsers.add_parser('run', help='Run complete pipeline')
    run_parser.add_argument('topic', help='Research topic')
    run_parser.add_argument('--max-papers', type=int, default=3, help='Maximum number of papers')
    
    # Search only
    search_parser = subparsers.add_parser('search', help='Search and download papers only')
    search_parser.add_argument('topic', help='Research topic')
    search_parser.add_argument('--max-papers', type=int, default=3, help='Maximum number of papers')
    
    # Extract only
    extract_parser = subparsers.add_parser('extract', help='Extract text only')
    extract_parser.add_argument('--pdf-dir', help='Directory with PDF files')
    
    # Analyze only
    analyze_parser = subparsers.add_parser('analyze', help='Analyze papers only')
    analyze_parser.add_argument('--extracted-dir', help='Directory with extracted text')
    
    # Draft only
    draft_parser = subparsers.add_parser('draft', help='Generate draft only')
    draft_parser.add_argument('topic', help='Research topic')
    draft_parser.add_argument('--analysis-dir', help='Directory with analysis files')
    
    # List files
    list_parser = subparsers.add_parser('list', help='List files in data directories')
    list_parser.add_argument('type', choices=['papers', 'extracted', 'analysis', 'drafts', 'all'],
                            help='Type of files to list')
    
    # Status
    status_parser = subparsers.add_parser('status', help='Check system status')
    
    # Clean
    clean_parser = subparsers.add_parser('clean', help='Clean data directories')
    clean_parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without deleting')
    clean_parser.add_argument('--type', choices=['papers', 'extracted', 'analysis', 'drafts', 'all'],
                             default='all', help='What to clean')
    
    args = parser.parse_args()
    
    # Create directories
    create_directories()
    
    # Check environment
    env_issues = check_environment()
    if env_issues:
        print("\n⚠️  Environment Issues Found:")
        for issue in env_issues:
            print(f"   • {issue}")
        print()
        
        if not any('API key' in issue for issue in env_issues):
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                sys.exit(1)
    
    # Execute commands
    if args.command == 'run':
        pipeline = ResearchReviewPipeline(args.topic, args.max_papers)
        pipeline.run_complete()
    
    elif args.command == 'search':
        print(f"\n🔍 Searching for papers on: {args.topic}")
        searcher = PaperSearcher()
        result = searcher.process_topic(args.topic)
        
        print(f"\nResult: {result['message']}")
        if result['papers']:
            print("\nDownloaded Papers:")
            for i, paper in enumerate(result['papers'], 1):
                print(f"{i}. {paper['title']}")
                print(f"   📍 {paper['local_path']}")
    
    elif args.command == 'extract':
        pdf_dir = Path(args.pdf_dir) if args.pdf_dir else PAPERS_DIR
        print(f"\n📄 Extracting text from PDFs in: {pdf_dir}")
        
        extractor = TextExtractor()
        saved_files = extractor.process_all_pdfs(pdf_dir)
        
        print(f"\n✅ Extracted {len(saved_files)} papers")
        for path in saved_files:
            print(f"   • {Path(path).name}")
    
    elif args.command == 'analyze':
        extracted_dir = Path(args.extracted_dir) if args.extracted_dir else EXTRACTED_DIR
        print(f"\n🔬 Analyzing papers from: {extracted_dir}")
        
        analyzer = PaperAnalyzer()
        analysis_paths = analyzer.process_all_papers(extracted_dir)
        
        print(f"\n✅ Analyzed {len(analysis_paths)} papers")
        for path in analysis_paths:
            print(f"   • {Path(path).name}")
    
    elif args.command == 'draft':
        print(f"\n✍️ Generating draft for topic: {args.topic}")
        
        generator = DraftGenerator()
        result = generator.generate_review(args.topic)
        
        print(f"\nResult: {result['message']}")
        if result['success']:
            print(f"Draft saved: {result['draft_path']}")
            
            print("\n📖 Draft Preview:")
            print("-" * 40)
            print(result['draft'][:500] + "...")
            print("-" * 40)
    
    elif args.command == 'list':
        print("\n📂 Data Directory Contents:\n")
        
        if args.type in ['papers', 'all']:
            papers = list(PAPERS_DIR.glob("*.pdf"))
            print(f"📚 Papers ({len(papers)}):")
            for p in papers[:10]:
                size = p.stat().st_size / (1024*1024)  # MB
                print(f"   • {p.name} ({size:.1f} MB)")
            if len(papers) > 10:
                print(f"   ... and {len(papers) - 10} more")
            print()
        
        if args.type in ['extracted', 'all']:
            extracted = list(EXTRACTED_DIR.glob("*.json"))
            print(f"📄 Extracted Text ({len(extracted)}):")
            for e in extracted[:10]:
                size = e.stat().st_size / 1024  # KB
                print(f"   • {e.name} ({size:.1f} KB)")
            if len(extracted) > 10:
                print(f"   ... and {len(extracted) - 10} more")
            print()
        
        if args.type in ['analysis', 'all']:
            analysis = list(ANALYSIS_DIR.glob("*_analysis.json"))
            print(f"🔬 Analysis ({len(analysis)}):")
            for a in analysis[:10]:
                size = a.stat().st_size / 1024  # KB
                print(f"   • {a.name} ({size:.1f} KB)")
            if len(analysis) > 10:
                print(f"   ... and {len(analysis) - 10} more")
            print()
        
        if args.type in ['drafts', 'all']:
            drafts = list(DRAFTS_DIR.glob("*.txt"))
            print(f"📝 Drafts ({len(drafts)}):")
            for d in drafts[:10]:
                size = d.stat().st_size / 1024  # KB
                modified = datetime.fromtimestamp(d.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                print(f"   • {d.name} ({size:.1f} KB) - {modified}")
            if len(drafts) > 10:
                print(f"   ... and {len(drafts) - 10} more")
            print()
    
    elif args.command == 'status':
        print("\n🔧 System Status\n")
        
        # Check directories
        print("📂 Directories:")
        for dir_path in [PAPERS_DIR, EXTRACTED_DIR, ANALYSIS_DIR, DRAFTS_DIR]:
            if dir_path.exists():
                files = list(dir_path.glob("*"))
                print(f"   ✅ {dir_path.name}: {len(files)} files")
            else:
                print(f"   ❌ {dir_path.name}: Missing")
        
        # Check API key
        from config import GEMINI_API_KEY
        if GEMINI_API_KEY and GEMINI_API_KEY != "your_google_gemini_api_key_here":
            print("\n🔑 API Key: ✅ Configured")
        else:
            print("\n🔑 API Key: ❌ Not configured")
        
        # Check Python version
        print(f"\n🐍 Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        
        # Check disk usage
        import shutil
        total, used, free = shutil.disk_usage(DATA_DIR)
        print(f"\n💾 Disk Usage:")
        print(f"   Total: {total // (2**30)} GB")
        print(f"   Used: {used // (2**30)} GB")
        print(f"   Free: {free // (2**30)} GB")
        print(f"   Data dir: {DATA_DIR}")
    
    elif args.command == 'clean':
        print(f"\n🧹 Cleaning data directories...")
        
        if args.dry_run:
            print("   DRY RUN - No files will be deleted\n")
        
        dirs_to_clean = []
        if args.type == 'papers' or args.type == 'all':
            dirs_to_clean.append(('papers', PAPERS_DIR, '*.pdf'))
        if args.type == 'extracted' or args.type == 'all':
            dirs_to_clean.append(('extracted', EXTRACTED_DIR, '*.json'))
        if args.type == 'analysis' or args.type == 'all':
            dirs_to_clean.append(('analysis', ANALYSIS_DIR, '*_analysis.json'))
        if args.type == 'drafts' or args.type == 'all':
            dirs_to_clean.append(('drafts', DRAFTS_DIR, '*.txt'))
        
        total_deleted = 0
        total_size = 0
        
        for name, directory, pattern in dirs_to_clean:
            files = list(directory.glob(pattern))
            if files:
                size = sum(f.stat().st_size for f in files)
                size_mb = size / (1024*1024)
                
                print(f"\n📁 {name.capitalize()}: {len(files)} files ({size_mb:.1f} MB)")
                
                if not args.dry_run:
                    for f in files:
                        f.unlink()
                        total_deleted += 1
                        total_size += f.stat().st_size
                        print(f"   🗑️ Deleted: {f.name}")
                else:
                    for f in files[:5]:
                        print(f"   📄 Would delete: {f.name}")
                    if len(files) > 5:
                        print(f"   ... and {len(files) - 5} more")
        
        if not args.dry_run:
            total_size_mb = total_size / (1024*1024)
            print(f"\n✅ Deleted {total_deleted} files ({total_size_mb:.1f} MB)")
        else:
            print("\n⚠️  Dry run complete - no files were deleted")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()