import os
import re
import markdown
import requests
from flask import Flask, render_template, request, jsonify, url_for, send_from_directory
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PyPDF2 import PdfReader
import docx

# ---------------- CONFIGURATION ----------------
load_dotenv()
app = Flask(__name__)

# Base Directory Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Unified folder for uploads & downloads so Analysis can find ALL files
UPLOAD_FOLDER = os.path.join(BASE_DIR, "papers") 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# API Keys & Configs
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- UPDATED MODEL ID ---
MODEL_ID = "gemini-3-flash-preview" 

# Semantic Scholar Config
SEMANTIC_API_KEY = "YOUR_API_KEY" 
SEMANTIC_BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

# Initialize Gemini Client
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    client = None

# ---------------- HELPER FUNCTIONS ----------------
def sanitize_filename(name):
    """Cleans up filenames to prevent path traversal or filesystem errors."""
    return re.sub(r'[\\/*?:"<>|]', "", name)[:60].strip()

def get_text_from_path(filepath):
    """Extracts text based on file extension (PDF, DOCX, TXT)."""
    try:
        if filepath.lower().endswith('.pdf'):
            reader = PdfReader(filepath)
            return " ".join([page.extract_text() or "" for page in reader.pages])
        elif filepath.lower().endswith('.docx'):
            doc = docx.Document(filepath)
            return "\n".join([p.text for p in doc.paragraphs])
        elif filepath.lower().endswith('.txt'):
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception as e:
        print(f"Extraction Error for {filepath}: {e}")
    return ""

# ---------------- VIEW ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analysis")
def analysis():
    return render_template("analysis.html")

@app.route("/query")
def query():
    return render_template("query.html")

@app.route("/files/<path:filename>")
def serve_file(filename):
    """Serves PDF files so they can be previewed in the browser."""
    return send_from_directory(UPLOAD_FOLDER, filename)

# ---------------- API: UPLOAD ----------------
@app.route("/api/upload", methods=["POST"])
def upload_api():
    files = request.files.getlist("file")
    uploaded_papers = []
    
    for f in files:
        if f and f.filename:
            filename = sanitize_filename(f.filename)
            path = os.path.join(UPLOAD_FOLDER, filename)
            f.save(path)
            
            uploaded_papers.append({
                "title": filename,
                "filename": filename,
                "meta": f"Size: {os.path.getsize(path) // 1024} KB",
                "url": url_for("serve_file", filename=filename)
            })
            
    return jsonify({"papers": uploaded_papers})

# ---------------- API: SEARCH & DOWNLOAD ----------------
@app.route('/api/search', methods=['POST'])
def search_papers():
    data = request.json
    topic = data.get('topic')
    downloaded_results = []

    if not topic:
        return jsonify({"error": "No topic provided"}), 400

    print(f"🔍 Searching for: {topic}...")

    # 1. Fetch Candidates
    headers = {"x-api-key": SEMANTIC_API_KEY}
    params = {"query": topic, "limit": 20, "fields": "title,year,authors,abstract,openAccessPdf,externalIds"}

    try:
        response = requests.get(SEMANTIC_BASE_URL, headers=headers, params=params)
        
        # Fallback to public API if key fails
        if response.status_code in [401, 403]:
            print("⚠️ API Key invalid or limited. Trying public access...")
            response = requests.get(SEMANTIC_BASE_URL, params=params)

        api_data = response.json().get("data", [])
        print(f"📄 Found {len(api_data)} candidates. Checking for PDFs...")
        
        count = 0
        for paper in api_data:
            if count >= 5: break # Stop after 5 successful downloads

            pdf_url = None
            
            # Strategy A: Direct OpenAccess Link
            if paper.get("openAccessPdf") and paper["openAccessPdf"].get("url"):
                pdf_url = paper["openAccessPdf"]["url"]
            
            # Strategy B: ArXiv Fallback
            elif paper.get("externalIds", {}).get("ArXiv"):
                pdf_url = f"https://arxiv.org/pdf/{paper['externalIds']['ArXiv']}.pdf"

            if pdf_url:
                try:
                    print(f"⬇️ Downloading: {paper['title'][:30]}...")
                    dl_headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    }
                    pdf_res = requests.get(pdf_url, headers=dl_headers, timeout=15)
                    
                    # Verify it's actually a PDF
                    if "application/pdf" in pdf_res.headers.get("Content-Type", "") or pdf_res.content[:4] == b'%PDF':
                        
                        clean_title = sanitize_filename(paper['title'])
                        file_name = f"{clean_title}.pdf"
                        file_path = os.path.join(UPLOAD_FOLDER, file_name)
                        
                        with open(file_path, "wb") as f: 
                            f.write(pdf_res.content)
                        
                        authors = [a["name"] for a in paper.get("authors", [])][:2]
                        
                        entry = {
                            "id": paper["paperId"],
                            "title": paper["title"],
                            "filename": file_name,
                            "meta": f"{paper.get('year', 'N/A')} • {', '.join(authors)}",
                            "url": url_for('serve_file', filename=file_name)
                        }
                        downloaded_results.append(entry)
                        count += 1
                        print("✅ Success!")
                    else:
                        print("❌ Failed: Not a PDF file.")
                except Exception as e:
                    print(f"❌ Failed to download: {e}")
                    continue
        
        if len(downloaded_results) == 0:
            return jsonify({"status": "success", "papers": [], "message": "No open-access PDFs found for this topic."})

        return jsonify({"status": "success", "papers": downloaded_results})

    except Exception as e:
        print(f"🔥 Critical Search Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------- API: ANALYZE (UPDATED COMPARISON LOGIC) ----------------
@app.route("/api/analyze", methods=["POST"])
def analyze_api():
    if not client:
         return jsonify({"status": "error", "message": "Gemini client not initialized. Check API Key."})

    filenames = request.json.get("files", [])
    combined_text = ""
    file_count = 0

    # 1. Extract Text
    for fname in filenames:
        path = os.path.join(UPLOAD_FOLDER, fname)
        if os.path.exists(path):
            raw_text = get_text_from_path(path)
            if raw_text.strip():
                file_count += 1
                combined_text += f"\n\n--- PAPER {file_count}: {fname} ---\n{raw_text[:50000]}"

    if not combined_text:
        return jsonify({"status": "error", "message": "No text could be extracted from the selected files."})

    try:
        # 2. Strict Comparison Prompt (UPDATED AS REQUESTED)
        system_instruction = (
            "You are an expert conducting a comparative literature review. "
            "Cross-paper comparison synthesizes insights across multiple research works. "
            "This step identifies similarities, differences, strengths, and limitations among papers."
        )

        user_prompt = f"""
        Compare the following research papers based on:
        1. Problem addressed
        2. Methodology
        3. Results
        4. Strengths
        5. Limitations
        
        Papers Content:
        {combined_text}
        
        Produce a structured comparative analysis output in Markdown.
        """

        # 3. Call Gemini
        response = client.models.generate_content(
            model=MODEL_ID, 
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3
            )
        )

        # 4. Render to HTML
        html_output = markdown.markdown(
            response.text, 
            extensions=['extra', 'tables', 'fenced_code', 'nl2br']
        )

        return jsonify({
            "status": "success",
            "html_content": html_output,
            "details": ["Comparative Analysis", "Structured Review Generated"]
        })

    except Exception as e:
        print(f"Gemini Analysis Error: {e}")
        return jsonify({"status": "error", "message": f"AI analysis failed: {str(e)}"})

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)