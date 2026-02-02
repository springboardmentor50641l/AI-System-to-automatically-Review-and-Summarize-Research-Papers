import requests, os
from config import PAPER_DIR

def download_pdf(url, filename):
    os.makedirs(PAPER_DIR, exist_ok=True)
    path = os.path.join(PAPER_DIR, f"{filename}.pdf")

    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()

        with open(path, "wb") as f:
            f.write(r.content)

        # Validate PDF by size
        if os.path.getsize(path) < 10_000:
            os.remove(path)
            return None

        return path

    except Exception:
        if os.path.exists(path):
            os.remove(path)
        return None
