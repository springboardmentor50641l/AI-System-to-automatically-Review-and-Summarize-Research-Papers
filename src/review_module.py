"""
review_module.py
Milestone 4: Review, Refinement, and Final Report Generation
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sys
import os

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from .config import Config
except ImportError:
    try:
        from src.config import Config
    except ImportError as e:
        print(f"❌ Import error: {e}")
        sys.exit(1)


class ReviewModule:
    """Review and refinement module for generated content"""
    
    def __init__(self):
        """Initialize review module"""
        self.review_dir = Config.DATA_DIR / "reviews"
        self.review_dir.mkdir(exist_ok=True)
        
    def load_latest_draft(self):
        """Load the most recent draft"""
        drafts_dir = Config.DRAFTS_DIR
        if not drafts_dir.exists():
            print("❌ No drafts directory found")
            return None
        
        draft_files = list(drafts_dir.glob("review_*.txt"))
        if not draft_files:
            print("❌ No draft files found")
            return None
        
        # Get most recent draft
        latest_draft = max(draft_files, key=lambda x: x.stat().st_mtime)
        
        try:
            with open(latest_draft, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"✅ Loaded draft: {latest_draft.name}")
            return {
                'file_path': str(latest_draft),
                'file_name': latest_draft.name,
                'content': content,
                'created': datetime.fromtimestamp(latest_draft.stat().st_mtime)
            }
        except Exception as e:
            print(f"❌ Error loading draft: {e}")
            return None
    
    def analyze_draft_quality(self, draft_content):
        """Analyze draft quality and provide suggestions"""
        analysis = {
            'word_count': 0,
            'section_count': 0,
            'sections_found': [],
            'issues': [],
            'suggestions': [],
            'score': 0
        }
        
        if not draft_content:
            return analysis
        
        # Basic metrics
        words = draft_content.split()
        analysis['word_count'] = len(words)
        
        # Check sections
        sections = re.findall(r'##\s+(.+)', draft_content)
        analysis['section_count'] = len(sections)
        analysis['sections_found'] = sections
        
        # Expected sections
        expected_sections = ['Abstract', 'Introduction', 'Methodology', 'Results', 
                           'Discussion', 'Conclusion', 'References']
        
        missing_sections = []
        for section in expected_sections:
            if not any(section.lower() in s.lower() for s in sections):
                missing_sections.append(section)
        
        if missing_sections:
            analysis['issues'].append(f"Missing sections: {', '.join(missing_sections)}")
            analysis['suggestions'].append(f"Add sections: {', '.join(missing_sections)}")
        
        # Check word count
        if analysis['word_count'] < 500:
            analysis['issues'].append("Draft is too short (less than 500 words)")
            analysis['suggestions'].append("Expand each section with more detail")
        elif analysis['word_count'] > 3000:
            analysis['issues'].append("Draft is too long (more than 3000 words)")
            analysis['suggestions'].append("Consider summarizing or removing redundant sections")
        
        # Check references
        if 'References' not in draft_content and 'references' not in draft_content.lower():
            analysis['issues'].append("References section missing")
            analysis['suggestions'].append("Add references section with proper citations")
        
        # Calculate quality score (0-100)
        score = 0
        
        # Section completeness (40 points)
        section_score = min(40, (analysis['section_count'] / len(expected_sections)) * 40)
        score += section_score
        
        # Word count (30 points)
        if 1000 <= analysis['word_count'] <= 2500:
            score += 30
        elif 500 <= analysis['word_count'] < 1000 or 2500 < analysis['word_count'] <= 3000:
            score += 20
        elif analysis['word_count'] > 0:
            score += 10
        
        # Structure (30 points)
        has_abstract = any('abstract' in s.lower() for s in sections)
        has_conclusion = any('conclusion' in s.lower() for s in sections)
        has_references = any('reference' in s.lower() for s in sections)
        
        structure_score = 0
        if has_abstract:
            structure_score += 10
        if has_conclusion:
            structure_score += 10
        if has_references:
            structure_score += 10
        score += structure_score
        
        analysis['score'] = min(100, int(score))
        
        # Generate suggestions based on score
        if analysis['score'] < 50:
            analysis['suggestions'].append("Consider major revisions: restructure, add missing sections, expand content")
        elif analysis['score'] < 75:
            analysis['suggestions'].append("Moderate revisions needed: improve section completeness and detail")
        else:
            analysis['suggestions'].append("Good draft! Minor edits may be needed for polish")
        
        return analysis
    
    def generate_revision_suggestions(self, draft_content, analysis):
        """Generate specific revision suggestions"""
        suggestions = []
        
        # Check for common issues
        lines = draft_content.split('\n')
        
        # Check line length
        long_lines = []
        for i, line in enumerate(lines, 1):
            if len(line) > 100 and line.strip() and not line.startswith('#'):
                long_lines.append((i, len(line)))
        
        if long_lines:
            suggestions.append(f"Consider breaking {len(long_lines)} long lines for better readability")
        
        # Check for placeholder text
        placeholders = ['TODO', 'FIXME', 'ADD HERE', 'INSERT', 'EXAMPLE']
        placeholder_lines = []
        for i, line in enumerate(lines, 1):
            if any(ph in line.upper() for ph in placeholders):
                placeholder_lines.append(i)
        
        if placeholder_lines:
            suggestions.append(f"Replace placeholder text on lines: {placeholder_lines}")
        
        # Check formatting
        if draft_content.count('\n\n\n') > 5:
            suggestions.append("Reduce excessive blank lines for cleaner formatting")
        
        # Add analysis-based suggestions
        suggestions.extend(analysis.get('suggestions', []))
        
        return suggestions
    
    def create_revised_draft(self, draft_content, suggestions):
        """Create a revised version of the draft"""
        revised = draft_content
        
        # Apply basic formatting improvements
        revised = re.sub(r'\n\n\n+', '\n\n', revised)  # Remove excessive blank lines
        
        # Add revision note
        revision_note = f"\n\n---\nREVISION NOTES ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):\n"
        for i, suggestion in enumerate(suggestions[:10], 1):  # Limit to 10 suggestions
            revision_note += f"{i}. {suggestion}\n"
        
        revised += revision_note
        
        return revised
    
    def prepare_final_report(self, draft_info, analysis, suggestions):
        """Prepare final report JSON"""
        report = {
            'project': 'AI Research Paper Reviewer',
            'milestone': 4,
            'generated_at': datetime.now().isoformat(),
            'draft_info': {
                'file_name': draft_info.get('file_name'),
                'created': draft_info.get('created').isoformat() if draft_info.get('created') else None,
                'word_count': analysis.get('word_count'),
                'section_count': analysis.get('section_count')
            },
            'quality_analysis': {
                'score': analysis.get('score'),
                'issues': analysis.get('issues', []),
                'sections_found': analysis.get('sections_found', [])
            },
            'revision_suggestions': suggestions,
            'status': 'completed',
            'next_steps': [
                'Review and implement suggested revisions',
                'Add specific citations from papers',
                'Format according to target publication guidelines',
                'Proofread for grammar and clarity'
            ]
        }
        
        return report
    
    def run_complete_review(self):
        """Run complete review cycle"""
        print(f"\n{'='*60}")
        print(f"🎯 MILESTONE 4: REVIEW & REFINEMENT")
        print(f"{'='*60}")
        
        # Step 1: Load latest draft
        print("\n📄 Step 1: Loading latest draft...")
        draft_info = self.load_latest_draft()
        
        if not draft_info:
            print("❌ No draft found. Run Milestone 3 first.")
            return False
        
        # Step 2: Analyze quality
        print("🔍 Step 2: Analyzing draft quality...")
        analysis = self.analyze_draft_quality(draft_info['content'])
        
        print(f"   📊 Quality Score: {analysis['score']}/100")
        print(f"   📝 Word Count: {analysis['word_count']}")
        print(f"   📑 Sections: {analysis['section_count']} found")
        
        if analysis['issues']:
            print(f"   ⚠️  Issues: {len(analysis['issues'])} found")
        
        # Step 3: Generate suggestions
        print("💡 Step 3: Generating revision suggestions...")
        suggestions = self.generate_revision_suggestions(draft_info['content'], analysis)
        
        print(f"   💡 Suggestions: {len(suggestions)} generated")
        for i, suggestion in enumerate(suggestions[:3], 1):  # Show top 3
            print(f"      {i}. {suggestion}")
        
        # Step 4: Create revised draft
        print("✍️  Step 4: Creating revised draft...")
        revised_content = self.create_revised_draft(draft_info['content'], suggestions)
        
        # Save revised draft
        original_path = Path(draft_info['file_path'])
        revised_filename = original_path.stem + "_revised" + original_path.suffix
        revised_path = self.review_dir / revised_filename
        
        with open(revised_path, 'w', encoding='utf-8') as f:
            f.write(revised_content)
        
        print(f"   ✅ Revised draft saved: {revised_filename}")
        
        # Step 5: Prepare final report
        print("📋 Step 5: Preparing final report...")
        final_report = self.prepare_final_report(draft_info, analysis, suggestions)
        
        # Save final report
        report_filename = f"final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.review_dir / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Final report saved: {report_filename}")
        
        # Step 6: Summary
        print("\n" + "="*60)
        print("📊 REVIEW COMPLETE - SUMMARY")
        print("="*60)
        
        print(f"\n📄 Original Draft: {draft_info['file_name']}")
        print(f"✍️  Revised Draft: {revised_filename}")
        print(f"📋 Final Report: {report_filename}")
        
        print(f"\n📊 Quality Metrics:")
        print(f"   Score: {analysis['score']}/100")
        print(f"   {'✅ Excellent' if analysis['score'] >= 80 else '⚠️  Good' if analysis['score'] >= 60 else '❌ Needs Work'}")
        print(f"   Sections: {analysis['section_count']}/7 expected sections")
        print(f"   Words: {analysis['word_count']} (1000-2500 recommended)")
        
        print(f"\n💡 Top Suggestions:")
        for i, suggestion in enumerate(suggestions[:5], 1):
            print(f"   {i}. {suggestion}")
        
        print(f"\n📁 Files saved in: {self.review_dir}")
        
        return True


def main():
    """Main function"""
    print("\n" + "="*60)
    print("           REVIEW & REFINEMENT MODULE")
    print("           Milestone 4")
    print("="*60)
    
    reviewer = ReviewModule()
    
    # Check if we have drafts
    drafts_dir = Config.DRAFTS_DIR
    if not drafts_dir.exists() or not list(drafts_dir.glob("*.txt")):
        print("❌ No draft files found.")
        print("\n💡 First run Milestone 3:")
        print("   python src/draft_generator.py")
        return
    
    # Run review
    success = reviewer.run_complete_review()
    
    if success:
        print(f"\n{'='*60}")
        print("🎉 MILESTONE 4 COMPLETE!")
        print("✅ Review cycle finished successfully")
        print("✅ Revised draft generated")
        print("✅ Final report created")
        print(f"{'='*60}")
        
        print("\n📝 Next Steps:")
        print("   1. Review the revised draft in data/reviews/")
        print("   2. Implement suggested revisions")
        print("   3. Add specific citations from your papers")
        print("   4. Format for final submission")
    else:
        print("\n❌ Review process failed")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()