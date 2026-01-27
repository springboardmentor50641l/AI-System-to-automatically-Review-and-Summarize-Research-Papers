"""
pipeline.py
Complete pipeline for Milestones 1-3
Runs search → extraction → analysis → draft generation in sequence
"""

import time
from datetime import datetime
from pathlib import Path

try:
    from src.paper_search import PaperSearchSystem
    from src.text_extractor import TextExtractor
    from src.paper_analyzer import PaperAnalyzer
    from src.draft_generator import DraftGenerator
    from src.config import Config
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.paper_search import PaperSearchSystem
    from src.text_extractor import TextExtractor
    from src.paper_analyzer import PaperAnalyzer
    from src.draft_generator import DraftGenerator
    from src.config import Config


class ResearchPipeline:
    """Complete research paper review pipeline"""
    
    def __init__(self, openai_api_key=None):
        """Initialize pipeline"""
        self.openai_key = openai_api_key
        self.topic = None
        self.start_time = None
        self.end_time = None
        
        # Initialize modules
        self.searcher = PaperSearchSystem()
        self.extractor = TextExtractor()
        self.analyzer = PaperAnalyzer(openai_api_key)
        self.generator = DraftGenerator(openai_api_key)
    
    def run_milestone1(self, topic):
        """Run Milestone 1: Search and download"""
        print(f"\n{'='*60}")
        print(f"🎯 MILESTONE 1: PAPER SEARCH & DOWNLOAD")
        print(f"{'='*60}")
        
        # Search for papers
        papers = self.searcher.search_papers(topic)
        
        if not papers:
            print("❌ No papers found. Try a different topic.")
            return False
        
        # Download papers
        downloaded_papers = self.searcher.download_papers(papers)
        
        if not downloaded_papers:
            print("❌ No PDFs downloaded.")
            return False
        
        # Save dataset
        self.searcher.create_dataset(downloaded_papers)
        
        print(f"✅ Milestone 1 complete: Downloaded {len(downloaded_papers)} papers")
        return True
    
    def run_milestone2(self):
        """Run Milestone 2: Text extraction and analysis"""
        print(f"\n{'='*60}")
        print(f"🎯 MILESTONE 2: TEXT EXTRACTION & ANALYSIS")
        print(f"{'='*60}")
        
        # Extract text from all PDFs
        print("\n📖 Extracting text from PDFs...")
        extracted_papers = self.extractor.process_all_papers()
        
        if not extracted_papers:
            print("❌ No text extracted.")
            return False
        
        # Analyze papers
        print("\n🔬 Analyzing papers...")
        analyses = self.analyzer.run_complete_analysis()
        
        if not analyses:
            print("❌ No analyses generated.")
            return False
        
        print(f"✅ Milestone 2 complete: Analyzed {len(extracted_papers)} papers")
        return True
    
    def run_milestone3(self, topic):
        """Run Milestone 3: Draft generation"""
        print(f"\n{'='*60}")
        print(f"🎯 MILESTONE 3: DRAFT GENERATION")
        print(f"{'='*60}")
        
        # Generate draft
        draft = self.generator.create_complete_draft(topic)
        
        if not draft:
            print("❌ No draft generated.")
            return False
        
        print(f"✅ Milestone 3 complete: Generated complete draft")
        return True
    
    def run_complete_pipeline(self, topic, openai_api_key=None):
        """Run complete pipeline from search to draft generation"""
        self.start_time = datetime.now()
        self.topic = topic
        
        print(f"\n{'='*60}")
        print(f"🚀 STARTING COMPLETE RESEARCH PIPELINE")
        print(f"📝 Topic: {topic}")
        print(f"⏰ Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Update OpenAI key if provided
        if openai_api_key:
            self.openai_key = openai_api_key
            self.analyzer.client = openai.OpenAI(api_key=openai_api_key)
            self.generator.client = openai.OpenAI(api_key=openai_api_key)
        
        results = {
            'topic': topic,
            'start_time': self.start_time.isoformat(),
            'milestones': {}
        }
        
        # Milestone 1
        milestone1_success = self.run_milestone1(topic)
        results['milestones']['milestone1'] = {
            'success': milestone1_success,
            'completed': datetime.now().isoformat()
        }
        
        if not milestone1_success:
            print("❌ Pipeline stopped at Milestone 1")
            return results
        
        # Milestone 2
        milestone2_success = self.run_milestone2()
        results['milestones']['milestone2'] = {
            'success': milestone2_success,
            'completed': datetime.now().isoformat()
        }
        
        if not milestone2_success:
            print("❌ Pipeline stopped at Milestone 2")
            return results
        
        # Milestone 3
        milestone3_success = self.run_milestone3(topic)
        results['milestones']['milestone3'] = {
            'success': milestone3_success,
            'completed': datetime.now().isoformat()
        }
        
        self.end_time = datetime.now()
        results['end_time'] = self.end_time.isoformat()
        results['duration_seconds'] = (self.end_time - self.start_time).total_seconds()
        
        print(f"\n{'='*60}")
        print(f"🎉 PIPELINE COMPLETE!")
        print(f"📝 Topic: {topic}")
        print(f"⏰ Duration: {results['duration_seconds']:.1f} seconds")
        print(f"✅ Milestones completed: 3/3")
        print(f"{'='*60}")
        
        return results


def main():
    """Run the complete pipeline"""
    print("\n" + "="*60)
    print("           COMPLETE RESEARCH PIPELINE")
    print("           Milestones 1-3 Integration")
    print("="*60)
    
    # Get topic
    topic = input("\n🔎 Enter research topic: ").strip()
    
    if not topic:
        print("❌ Please enter a topic")
        print("\n💡 Example topics:")
        print("   • machine learning in healthcare")
        print("   • deep learning for medical imaging")
        print("   • natural language processing applications")
        return
    
    # Get OpenAI API key
    openai_key = None
    if Config.OPENAI_API_KEY:
        openai_key = Config.OPENAI_API_KEY
        print(f"\n✅ Using OpenAI API key from .env file")
    else:
        print("\n⚠️  OpenAI API key not found in .env file")
        openai_key = input("   Enter OpenAI API key (required for Milestone 3): ").strip()
    
    if not openai_key:
        print("❌ OpenAI API key required for complete pipeline")
        print("   You can run up to Milestone 2 without it")
        run_without_ai = input("   Run without AI (Milestones 1-2 only)? (y/n): ").lower().strip()
        if run_without_ai != 'y':
            return
    
    # Run pipeline
    pipeline = ResearchPipeline(openai_api_key=openai_key)
    results = pipeline.run_complete_pipeline(topic, openai_key)
    
    # Summary
    print(f"\n📊 PIPELINE RESULTS:")
    for milestone, data in results['milestones'].items():
        status = "✅ SUCCESS" if data['success'] else "❌ FAILED"
        print(f"   {milestone.upper()}: {status}")
    
    print(f"\n📁 Output directories:")
    print(f"   📄 PDFs: {Config.PAPERS_DIR}")
    print(f"   📝 Extracted text: {Config.DATA_DIR}/extracted_text")
    print(f"   🔬 Analysis: {Config.DATA_DIR}/analysis")
    print(f"   📋 Drafts: {Config.DATA_DIR}/drafts")


if __name__ == "__main__":
    main()