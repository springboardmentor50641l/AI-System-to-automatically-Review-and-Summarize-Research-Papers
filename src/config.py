import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class"""
    
    # API Configuration
    API_KEY = os.getenv('SEMANTIC_SCHOLAR_API_KEY', '').strip()
    API_BASE_URL = "https://api.semanticscholar.org/graph/v1"
    TIMEOUT = 30
    
    # File paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    PAPERS_DIR = DATA_DIR / "papers"
    METADATA_DIR = DATA_DIR / "metadata"
    DATASET_FILE = DATA_DIR / "dataset.json"

def setup_directories():
    """Create necessary directories"""
    Config.DATA_DIR.mkdir(exist_ok=True)
    Config.PAPERS_DIR.mkdir(exist_ok=True)
    Config.METADATA_DIR.mkdir(exist_ok=True)
    return True

def get_api_headers():
    """Get API headers"""
    headers = {
        'User-Agent': 'ResearchPaperCollector/1.0',
        'Accept': 'application/json'
    }
    if Config.API_KEY:
        headers['x-api-key'] = Config.API_KEY
    return headers

if __name__ == "__main__":
    setup_directories()
    print("✅ Configuration loaded successfully")