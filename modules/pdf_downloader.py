import requests
import os

def download_pdf(url, filename):
    os.makedirs("data/papers", exist_ok=True)
    r = requests.get(url, timeout=20)
    with open(f"data/papers/{filename}.pdf", "wb") as f:
        f.write(r.content)
