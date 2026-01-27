"""
paper_analyzer.py - SIMPLIFIED WORKING VERSION
Milestone 2: Paper Analysis Module
"""

import json
import re
import nltk
from pathlib import Path
from datetime import datetime
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.config import Config
except ImportError:
    print("❌ Cannot import Config")
    sys.exit(1)

class WorkingPaperAnalyzer:
    """Working paper analyzer without dependencies"""
    
    def __init__(self):
        self.analysis_dir = Config.DATA_DIR / "analysis"
        self.analysis_dir.mkdir(exist_ok=True)
        
        # Setup NLTK
        try:
            nltk.data.find("tokenizers/punkt")
            nltk.data.find("corpora/stopwords")
        except:
            print("📥 Downloading NLTK data...")
            nltk.download("punkt", quiet=True)
            nltk.download("stopwords", quiet=True)
    
    def analyze_papers(self):
        """Main analysis function"""
        print(f"\n{'='*60}")
        print("🔬 PAPER ANALYSIS STARTING")
        print(f"{'='*60}")
        
        # Load extracted papers
        extracted_dir = Config.DATA_DIR / "extracted_text"
        if not extracted_dir.exists():
            print("❌ No extracted papers found")
            return []
        
        files = list(extracted_dir.glob("*_extracted.json"))
        print(f"📂 Found {len(files)} extracted papers")
        
        results = []
        for file_path in files[:3]:  # Limit to 3 for demo
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data.get('total_pages', 0) == 0:
                    continue
                
                # Simple analysis
                analysis = {
                    'file_name': data.get('file_name'),
                    'pages': data.get('total_pages', 0),
                    'words': data.get('total_words', 0),
                    'analysis_date': datetime.now().isoformat()
                }
                
                # Extract some text for keywords
                if 'pages' in data and data['pages']:
                    text = data['pages'][0].get('text', '')[:1000]
                    words = nltk.word_tokenize(text.lower())
                    words = [w for w in words if w.isalnum() and len(w) > 2]
                    
                    # Count frequencies
                    freq = Counter(words)
                    analysis['top_keywords'] = [word for word, count in freq.most_common(10)]
                
                # Save analysis
                output_file = self.analysis_dir / f"{Path(file_path).stem}_analysis.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, indent=2)
                
                results.append(analysis)
                print(f"✅ Analyzed: {analysis['file_name'][:40]}...")
                
            except Exception as e:
                print(f"❌ Error analyzing {file_path.name}: {e}")
        
        # Generate summary
        if results:
            summary_file = self.analysis_dir / "analysis_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'total_papers_analyzed': len(results),
                    'analysis_date': datetime.now().isoformat(),
                    'papers': results
                }, f, indent=2)
            
            print(f"\n📊 ANALYSIS SUMMARY:")
            print(f"   Papers analyzed: {len(results)}")
            print(f"   Results saved in: {self.analysis_dir}")
        
        return results

def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("           WORKING PAPER ANALYZER")
    print("="*60)
    
    analyzer = WorkingPaperAnalyzer()
    results = analyzer.analyze_papers()
    
    if results:
        print(f"\n{'='*60}")
        print("🎉 MILESTONE 2 PART 2 COMPLETE!")
        print(f"{'='*60}")
        
        # Show sample
        print(f"\n📋 Sample from first paper:")
        print(f"   File: {results[0]['file_name'][:50]}...")
        if 'top_keywords' in results[0]:
            print(f"   Keywords: {', '.join(results[0]['top_keywords'][:5])}")

if __name__ == "__main__":
    main()