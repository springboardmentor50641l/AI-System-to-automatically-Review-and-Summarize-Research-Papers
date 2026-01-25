from flask import Flask, render_template, request
import requests
import json
import os
import re

app = Flask(__name__)

# --- CONFIGURATION & DIRECTORIES ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_FILE = os.path.join(BASE_DIR, "dataset.json")
PDF_FOLDER = os.path.join(BASE_DIR, "papers")
os.makedirs(PDF_FOLDER, exist_ok=True)

# API CONFIG (Semantic Scholar)
API_KEY = "LoJ8uOb4J7aWQ6VLyN2ry1y4dGNyA8zI8s0XRfIL"
BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

def load_dataset():
    if not os.path.exists(DATASET_FILE): return []
    try:
        with open(DATASET_FILE, "r") as f:
            return json.loads(f.read())
    except: return []

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "", title)[:50]

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    status_message = ""

    if request.method == "POST":
        topic = request.form.get("topic")
        
        # 1. Automated Paper Search
        headers = {"x-api-key": API_KEY}
        params = {
            "query": topic,
            "limit": 8,
            "fields": "title,year,authors,abstract,openAccessPdf,externalIds"
        }

        try:
            response = requests.get(BASE_URL, headers=headers, params=params)
            api_data = response.json().get("data", [])
            dataset = load_dataset()

            # 2. Paper Selection & PDF Download
            for paper in api_data:
                # Select only if it has an Open Access PDF
                pdf_url = None
                if paper.get("openAccessPdf") and paper["openAccessPdf"].get("url"):
                    pdf_url = paper["openAccessPdf"]["url"]
                elif paper.get("externalIds", {}).get("ArXiv"):
                    pdf_url = f"https://arxiv.org/pdf/{paper['externalIds']['ArXiv']}.pdf"

                if pdf_url:
                    try:
                        # Attempt Download
                        pdf_res = requests.get(pdf_url, timeout=10)
                        if "pdf" in pdf_res.headers.get("Content-Type", "").lower():
                            file_name = f"{sanitize_filename(paper['title'])}.pdf"
                            file_path = os.path.join(PDF_FOLDER, file_name)
                            
                            with open(file_path, "wb") as f:
                                f.write(pdf_res.content)

                            # 3. Dataset Preparation
                            # Creating a clean entry with reasoning
                            entry = {
                                "title": paper["title"],
                                "year": paper.get("year"),
                                "authors": [a["name"] for a in paper.get("authors", [])],
                                "local_path": file_path,
                                "selection_reason": f"Matches query '{topic}' and provided full-text PDF access."
                            }
                            dataset.append(entry)
                            results.append(entry)
                    except:
                        continue

            with open(DATASET_FILE, "w") as f:
                json.dump(dataset, f, indent=4)
            
            status_message = f"Success: {len(results)} papers added to dataset." if results else "No downloadable papers found."
        
        except Exception as e:
            status_message = f"Error: {str(e)}"

    return render_template("index.html", papers=results, message=status_message)

if __name__ == "__main__":
    app.run(debug=True)