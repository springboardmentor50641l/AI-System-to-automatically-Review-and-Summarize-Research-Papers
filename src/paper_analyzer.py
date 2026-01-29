"""
paper_analyzer.py - SIMPLIFIED WORKING VERSION
Milestone 2: Paper Analysis Module
Analyzes extracted text and identifies key findings
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
    from src.utils import clean_text_for_display
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Trying alternative import...")
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.config import Config
    from src.utils import clean_text_for_display


class PaperAnalyzer:
    """Analyzes research papers for key findings and patterns"""
    
    def __init__(self):
        """Initialize analyzer"""
        self.analysis_dir = Config.ANALYSIS_DIR
        self.analysis_dir.mkdir(exist_ok=True)
        
        # Setup NLTK
        try:
            nltk.data.find("tokenizers/punkt")
            nltk.data.find("corpora/stopwords")
        except:
            print("📥 Downloading NLTK data...")
            nltk.download("punkt", quiet=True)
            nltk.download("stopwords", quiet=True)
        
        # Academic stopwords (common words to ignore)
        self.stop_words = set(nltk.corpus.stopwords.words('english'))
        academic_stopwords = {'paper', 'study', 'research', 'result', 'method', 'approach', 
                             'propose', 'proposed', 'show', 'shown', 'use', 'using', 'used',
                             'figure', 'table', 'section', 'chapter', 'example', 'et', 'al',
                             'also', 'however', 'therefore', 'thus', 'hence', 'furthermore'}
        self.stop_words.update(academic_stopwords)
    
    def load_extracted_papers(self):
        """Load papers from extracted text directory"""
        extracted_dir = Config.EXTRACTED_TEXT_DIR
        if not extracted_dir.exists():
            print("❌ No extracted papers found")
            print(f"📁 Directory: {extracted_dir}")
            return []
        
        files = list(extracted_dir.glob("*_extracted.json"))
        if not files:
            print("❌ No extracted JSON files found")
            print("💡 Run text extraction first: python -m src.text_extraction")
            return []
        
        print(f"📂 Found {len(files)} extracted papers")
        
        papers = []
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Basic validation
                if not data or 'total_words' not in data or data['total_words'] < 10:
                    print(f"⚠️  Skipping {file_path.name}: insufficient text")
                    continue
                
                papers.append(data)
                print(f"✅ Loaded: {data.get('file_name', 'Unknown')}")
                
            except Exception as e:
                print(f"❌ Error loading {file_path.name}: {e}")
        
        return papers
    
    def extract_keywords(self, text, n_keywords=15):
        """Extract keywords from text using TF-IDF-like approach"""
        if not text or len(text) < 100:
            return []
        
        # Tokenize and clean
        words = nltk.word_tokenize(text.lower())
        words = [w for w in words if w.isalnum() and len(w) > 2 and w not in self.stop_words]
        
        # Count frequencies
        word_freq = Counter(words)
        
        # Get most common words
        common_words = word_freq.most_common(n_keywords * 2)  # Get more for filtering
        
        # Filter out overly common academic words
        filtered_keywords = []
        academic_common = {'analysis', 'model', 'system', 'data', 'problem', 'solution',
                          'algorithm', 'technique', 'framework', 'process', 'approach'}
        
        for word, count in common_words:
            if word not in academic_common and len(word) > 3:
                filtered_keywords.append(word)
            if len(filtered_keywords) >= n_keywords:
                break
        
        return filtered_keywords
    
    def extract_key_findings(self, text):
        """Extract potential key findings from text"""
        if not text:
            return []
        
        # Look for sentences that might contain findings
        sentences = nltk.sent_tokenize(text)
        
        key_findings = []
        finding_indicators = ['show that', 'demonstrate that', 'find that', 'conclude that',
                            'results indicate', 'evidence suggests', 'our analysis shows',
                            'we found', 'we demonstrate', 'significant', 'improved',
                            'increased', 'decreased', 'better than', 'outperforms']
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check if sentence contains finding indicators
            if any(indicator in sentence_lower for indicator in finding_indicators):
                # Clean and shorten if too long
                if len(sentence) > 200:
                    sentence = sentence[:200] + "..."
                key_findings.append(sentence.strip())
        
        return key_findings[:5]  # Return top 5
    
    def calculate_similarity(self, papers):
        """Calculate similarity between papers"""
        if len(papers) < 2:
            return {}
        
        # Extract text for each paper
        paper_texts = []
        for paper in papers:
            # Combine sections if available
            if 'sections' in paper and paper['sections']:
                combined = ' '.join([str(v) for v in paper['sections'].values() if v])
            else:
                # Fallback to page text
                combined = ' '.join([page.get('text', '') for page in paper.get('pages', [])])
            paper_texts.append(combined[:5000])  # Limit text length
        
        # Calculate TF-IDF and cosine similarity
        try:
            vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            tfidf_matrix = vectorizer.fit_transform(paper_texts)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Prepare results
            results = []
            for i in range(len(papers)):
                for j in range(i + 1, len(papers)):
                    similarity = similarity_matrix[i, j]
                    results.append({
                        'paper1': papers[i].get('file_name', f'Paper_{i+1}'),
                        'paper2': papers[j].get('file_name', f'Paper_{j+1}'),
                        'similarity': round(float(similarity), 3)
                    })
            
            return {'pairwise_similarities': results}
            
        except Exception as e:
            print(f"⚠️  Similarity calculation failed: {e}")
            return {}
    
    def analyze_paper(self, paper_data):
        """Analyze a single paper"""
        analysis = {
            'file_name': paper_data.get('file_name', 'Unknown'),
            'paper_title': Path(paper_data.get('file_name', '')).stem,
            'extraction_method': paper_data.get('extraction_method', 'unknown'),
            'total_pages': paper_data.get('total_pages', 0),
            'total_words': paper_data.get('total_words', 0),
            'total_chars': paper_data.get('total_chars', 0),
            'analysis_date': datetime.now().isoformat(),
            'sections_found': [],
            'key_findings': [],
            'methodology_hints': []
        }
        
        # Extract combined text
        combined_text = ""
        
        # Try to get text from sections first
        if 'sections' in paper_data and paper_data['sections']:
            sections = paper_data['sections']
            analysis['sections_found'] = [k for k, v in sections.items() if v and len(str(v).strip()) > 0]
            
            # Combine all section text
            for section_text in sections.values():
                if section_text:
                    combined_text += str(section_text) + " "
            
            # Look for methodology hints
            if sections.get('methodology'):
                methodology_text = sections['methodology'][:1000]
                analysis['methodology_hints'] = self.extract_methodology_hints(methodology_text)
        
        # Fallback to page text
        if not combined_text or len(combined_text) < 100:
            for page in paper_data.get('pages', []):
                page_text = page.get('text', '')
                if page_text:
                    combined_text += page_text + " "
        
        # Extract keywords if we have enough text
        if len(combined_text) > 100:
            analysis['keywords'] = self.extract_keywords(combined_text)
            analysis['key_findings'] = self.extract_key_findings(combined_text)
            
            # Calculate readability metrics
            words = nltk.word_tokenize(combined_text)
            sentences = nltk.sent_tokenize(combined_text)
            
            if sentences and words:
                analysis['avg_sentence_length'] = round(len(words) / len(sentences), 1)
                analysis['vocabulary_size'] = len(set(words))
        
        return analysis
    
    def extract_methodology_hints(self, methodology_text):
        """Extract hints about methodology from text"""
        if not methodology_text:
            return []
        
        hints = []
        methodology_indicators = [
            ('experiment', ['experiment', 'experimental', 'trial']),
            ('survey', ['survey', 'questionnaire', 'interview']),
            ('simulation', ['simulation', 'model', 'modeling']),
            ('case study', ['case study', 'case analysis']),
            ('statistical', ['statistical', 'regression', 'correlation', 'anova']),
            ('machine learning', ['neural network', 'deep learning', 'machine learning', 'ai']),
            ('qualitative', ['qualitative', 'thematic analysis', 'content analysis']),
            ('quantitative', ['quantitative', 'measurement', 'metric'])
        ]
        
        text_lower = methodology_text.lower()
        for method_name, indicators in methodology_indicators:
            if any(indicator in text_lower for indicator in indicators):
                hints.append(method_name)
        
        return hints[:5]
    
    def run_complete_analysis(self):
        """Run analysis on all extracted papers"""
        print(f"\n{'='*60}")
        print("🔬 PAPER ANALYSIS STARTING")
        print(f"{'='*60}")
        
        # Load papers
        papers = self.load_extracted_papers()
        if not papers:
            return []
        
        print(f"\n📊 Analyzing {len(papers)} papers...")
        
        all_analyses = []
        
        # Analyze each paper
        for i, paper in enumerate(papers, 1):
            print(f"\n📄 Analyzing paper {i}/{len(papers)}: {paper.get('file_name', 'Unknown')}")
            
            analysis = self.analyze_paper(paper)
            all_analyses.append(analysis)
            
            # Show quick summary
            if analysis.get('keywords'):
                print(f"   🔑 Keywords: {', '.join(analysis['keywords'][:5])}")
            if analysis.get('key_findings'):
                print(f"   💡 Findings: {len(analysis['key_findings'])} identified")
        
        # Calculate similarities between papers
        if len(papers) > 1:
            print(f"\n🔗 Calculating similarities between papers...")
            similarity_results = self.calculate_similarity(papers)
            if similarity_results:
                print(f"   📈 Similarity analysis complete")
        
        # Save individual analyses
        for analysis in all_analyses:
            try:
                # Create safe filename
                safe_name = re.sub(r'[^\w\s-]', '', analysis['file_name'])
                safe_name = re.sub(r'\s+', '_', safe_name)
                output_file = self.analysis_dir / f"{safe_name[:40]}_analysis.json"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Saved analysis: {output_file.name}")
                
            except Exception as e:
                print(f"❌ Error saving analysis: {e}")
        
        # Generate summary report
        self.generate_summary_report(all_analyses, similarity_results if 'similarity_results' in locals() else {})
        
        print(f"\n{'='*60}")
        print("🎉 ANALYSIS COMPLETE!")
        print(f"{'='*60}")
        
        return all_analyses
    
    def generate_summary_report(self, analyses, similarity_results):
        """Generate a summary report of all analyses"""
        try:
            summary = {
                'total_papers_analyzed': len(analyses),
                'analysis_date': datetime.now().isoformat(),
                'papers': [],
                'overall_statistics': {
                    'total_words': sum(a.get('total_words', 0) for a in analyses),
                    'total_pages': sum(a.get('total_pages', 0) for a in analyses),
                    'avg_words_per_paper': round(sum(a.get('total_words', 0) for a in analyses) / max(len(analyses), 1), 0)
                },
                'similarity_analysis': similarity_results
            }
            
            # Add paper summaries
            for analysis in analyses:
                paper_summary = {
                    'file_name': analysis.get('file_name'),
                    'keywords': analysis.get('keywords', [])[:10],
                    'key_findings_count': len(analysis.get('key_findings', [])),
                    'methodology_hints': analysis.get('methodology_hints', []),
                    'word_count': analysis.get('total_words', 0)
                }
                summary['papers'].append(paper_summary)
            
            # Find common keywords across papers
            all_keywords = []
            for analysis in analyses:
                all_keywords.extend(analysis.get('keywords', []))
            
            keyword_freq = Counter(all_keywords)
            summary['common_keywords'] = keyword_freq.most_common(10)
            
            # Save summary
            summary_file = self.analysis_dir / "analysis_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            print(f"\n📊 ANALYSIS SUMMARY:")
            print(f"   📄 Papers analyzed: {summary['total_papers_analyzed']}")
            print(f"   📝 Total words: {summary['overall_statistics']['total_words']:,}")
            print(f"   📑 Total pages: {summary['overall_statistics']['total_pages']}")
            
            if summary['common_keywords']:
                print(f"\n   🔑 Common keywords across papers:")
                for keyword, freq in summary['common_keywords'][:5]:
                    print(f"      • {keyword} ({freq} papers)")
            
            print(f"\n📁 Results saved in: {self.analysis_dir}")
            
        except Exception as e:
            print(f"❌ Error generating summary: {e}")


def main():
    """Main entry point for paper analyzer"""
    print("\n" + "="*60)
    print("           PAPER ANALYZER")
    print("           Milestone 2: Part 2")
    print("="*60)
    
    analyzer = PaperAnalyzer()
    
    # Check if we have extracted papers
    extracted_dir = Config.EXTRACTED_TEXT_DIR
    if not extracted_dir.exists() or not list(extracted_dir.glob("*_extracted.json")):
        print("❌ No extracted papers found")
        print("\n💡 First run text extraction:")
        print("   python -m src.text_extraction")
        print("\n   Or run complete pipeline:")
        print("   python -m src.pipeline")
        return
    
    # Run analysis
    results = analyzer.run_complete_analysis()
    
    if results:
        print(f"\n📋 Sample from first paper analysis:")
        if results[0].get('keywords'):
            print(f"   🔑 Keywords: {', '.join(results[0]['keywords'][:5])}")
        if results[0].get('key_findings'):
            print(f"   💡 Sample finding: {results[0]['key_findings'][0][:100]}...")
        
        print(f"\n🎯 MILESTONE 2 PART 2 COMPLETE!")
        print(f"\n📁 Analysis saved in: {analyzer.analysis_dir}")
        print(f"\n📋 Next Steps (Milestone 3):")
        print("   • Generate review draft: python -m src.draft_generator")
        print("   • Or run complete pipeline: python -m src.pipeline")
    else:
        print("❌ No papers were analyzed")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()