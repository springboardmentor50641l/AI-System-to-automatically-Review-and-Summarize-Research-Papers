"""
Utility functions for the Automated Research Review System.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger
import tiktoken

# FIX: Import from config properly
from config import LOGS_DIR, LOG_LEVEL

def setup_logging():
    """Configure logging for the application."""
    
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sink=lambda msg: print(msg),
        level=LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Add file handler
    log_file = LOGS_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    logger.add(
        sink=str(log_file),
        level=LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    return logger

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count the number of tokens in a text string."""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback: rough estimate (4 chars per token)
        return len(text) // 4

def chunk_text(text: str, max_tokens: int = 30000) -> list:
    """Split text into chunks of approximately max_tokens."""
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    # Split by paragraphs to maintain coherence
    paragraphs = text.split('\n\n')
    
    for para in paragraphs:
        para_tokens = count_tokens(para)
        
        if current_tokens + para_tokens > max_tokens and current_chunk:
            # Save current chunk
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_tokens = para_tokens
        else:
            current_chunk.append(para)
            current_tokens += para_tokens
    
    # Add last chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

def safe_json_loads(json_str: str) -> Dict[str, Any]:
    """Safely load JSON string with error handling."""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        # Try to extract JSON from markdown code blocks
        import re
        json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        matches = re.findall(json_pattern, json_str)
        if matches:
            try:
                return json.loads(matches[0])
            except:
                pass
        return {}

def generate_file_hash(file_path: Path) -> str:
    """Generate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters."""
    import re
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:195] + '...' + ('.' + ext if ext else '')
    return filename

def format_progress_message(step: str, status: str, details: str = "") -> str:
    """Format progress messages for UI display."""
    icons = {
        "start": "🚀",
        "search": "🔍",
        "download": "📥",
        "extract": "📄",
        "analyze": "🔬",
        "draft": "✍️",
        "complete": "✅",
        "error": "❌",
        "warning": "⚠️"
    }
    
    icon = icons.get(step.lower(), "•")
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    message = f"[{timestamp}] {icon} {status}"
    if details:
        message += f"\n   📌 {details}"
    
    return message