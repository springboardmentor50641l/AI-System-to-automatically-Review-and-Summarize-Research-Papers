__version__ = "1.0.0"
__author__ = "Research Paper Reviewer Team"

# Export main components
from .config import Config
from .paper_search import PaperSearchSystem
from .text_extraction import TextExtractor
from .paper_analyzer import PaperAnalyzer
from .draft_generator import DraftGenerator
from .pipeline import ResearchPipeline

__all__ = [
    'Config',
    'PaperSearchSystem',
    'TextExtractor',
    'PaperAnalyzer',
    'DraftGenerator',
    'ResearchPipeline'
]