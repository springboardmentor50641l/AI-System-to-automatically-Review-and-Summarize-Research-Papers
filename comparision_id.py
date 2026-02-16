from datetime import datetime

def generate_comparison_id() -> str:
    return datetime.now().strftime("comparison_%Y%m%d_%H%M%S")