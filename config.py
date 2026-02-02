import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-flash-latest")
MAX_PAPERS = int(os.getenv("MAX_PAPERS", 3))

PAPER_DIR = "data/papers"
OUTPUT_DIR = "data/outputs"
