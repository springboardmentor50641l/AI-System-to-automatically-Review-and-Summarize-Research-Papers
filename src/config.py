"""
config.py - Complete configuration file for Research Paper Reviewer
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the entire system"""
    
    # API Configuration
    SEMANTIC_SCHOLAR_API_KEY = os.getenv('SEMANTIC_SCHOLAR_API_KEY', '').strip()
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '').strip()
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '').strip()
    
    # API URLs
    API_BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    # Timeout settings
    TIMEOUT = 45
    DOWNLOAD_TIMEOUT = 60
    
    # File paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    PAPERS_DIR = DATA_DIR / "papers"
    METADATA_DIR = DATA_DIR / "metadata"
    EXTRACTED_TEXT_DIR = DATA_DIR / "extracted_text"
    ANALYSIS_DIR = DATA_DIR / "analysis"
    DRAFTS_DIR = DATA_DIR / "drafts"
    DATASET_FILE = DATA_DIR / "dataset.json"
    
    # Model settings
    DEFAULT_GPT_MODEL = "gpt-3.5-turbo"
    DEFAULT_GEMINI_MODEL = "gemini-1.5-pro"
    
    # Limits
    MAX_PAPERS_TO_DOWNLOAD = 3
    MAX_PAPERS_TO_ANALYZE = 3
    MAX_TOKENS_FOR_GPT = 1000
    
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
            directory.mkdir(parents=True, exist_ok=True)
        
        print("✅ Created/verified all directories")
        return True
    
    @classmethod
    def validate_api_keys(cls):
        """Validate that required API keys are present"""
        missing_keys = []
        
        if not cls.SEMANTIC_SCHOLAR_API_KEY:
            missing_keys.append("SEMANTIC_SCHOLAR_API_KEY")
        
        if not cls.OPENAI_API_KEY:
            print("⚠️  OPENAI_API_KEY not found. Milestone 3 will use template mode.")
        
        return missing_keys


def get_api_headers():
    """Get API headers for Semantic Scholar"""
    headers = {
        'User-Agent': 'ResearchPaperReviewer/1.0 (https://github.com/your-repo)',
        'Accept': 'application/json'
    }
    if Config.SEMANTIC_SCHOLAR_API_KEY:
        headers['x-api-key'] = Config.SEMANTIC_SCHOLAR_API_KEY
    return headers


if __name__ == "__main__":
    # Test configuration
    Config.setup_directories()
    missing = Config.validate_api_keys()
    
    if missing:
        print(f"⚠️  Missing API keys: {', '.join(missing)}")
        print("   Add them to your .env file")
    else:
        print("✅ Configuration loaded successfully")
    
    print(f"\n📁 Data directory: {Config.DATA_DIR}")
    print(f"📄 Papers directory: {Config.PAPERS_DIR}")
    print(f"📝 Extracted text: {Config.EXTRACTED_TEXT_DIR}")
    print(f"🔬 Analysis: {Config.ANALYSIS_DIR}")
    print(f"✍️  Drafts: {Config.DRAFTS_DIR}")