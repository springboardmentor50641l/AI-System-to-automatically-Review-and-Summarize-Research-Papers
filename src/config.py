"""
config.py - Complete configuration file
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class"""
    
    # API Configuration
    SEMANTIC_SCHOLAR_API_KEY = os.getenv('SEMANTIC_SCHOLAR_API_KEY', '').strip()
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '').strip()
    API_BASE_URL = "https://api.semanticscholar.org/graph/v1"
    TIMEOUT = 30
    
    # File paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    PAPERS_DIR = DATA_DIR / "papers"
    METADATA_DIR = DATA_DIR / "metadata"
    EXTRACTED_TEXT_DIR = DATA_DIR / "extracted_text"
    ANALYSIS_DIR = DATA_DIR / "analysis"
    DRAFTS_DIR = DATA_DIR / "drafts"
    DATASET_FILE = DATA_DIR / "dataset.json"
    
    @classmethod
    def setup_directories(cls):
        """Create all necessary directories"""
        directories = [
            cls.DATA_DIR,
            cls.PAPERS_DIR,
            cls.METADATA_DIR,
            cls.EXTRACTED_TEXT_DIR,
            cls.ANALYSIS_DIR,
            cls.DRAFTS_DIR
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
        
        print(f"✅ Created/verified all directories")
        return True

def get_api_headers():
    """Get API headers for Semantic Scholar"""
    headers = {
        'User-Agent': 'ResearchPaperReviewer/1.0',
        'Accept': 'application/json'
    }
    if Config.SEMANTIC_SCHOLAR_API_KEY:
        headers['x-api-key'] = Config.SEMANTIC_SCHOLAR_API_KEY
    return headers

if __name__ == "__main__":
    Config.setup_directories()
    print("✅ Configuration loaded successfully")