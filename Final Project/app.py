import os
import re
import markdown
import requests
from flask import Flask, render_template, request, jsonify, url_for, send_from_directory
from dotenv import load_dotenv

# --- LangGraph & LangChain Imports ---
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

# --- PDF/File Handling ---
from PyPDF2 import PdfReader
import docx

# ---------------- CONFIGURATION ----------------
load_dotenv()
app = Flask(__name__)

# Base Directory Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "papers")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SEMANTIC_API_KEY = os.getenv("SEMANTIC_API_KEY", "") 
SEMANTIC_BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

# ---------------- INITIALIZE GEMINI ----------------
# Using Gemini 3.0 Preview as requested.
# Note: This model often returns structured dictionaries instead of plain text strings.
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview", 
    google_api_key=GEMINI_API_KEY,
    temperature=0.3,
    max_output_tokens=8192
)

# ---------------- LANGGRAPH SETUP ----------------

# 1. Define the State
class ResearchState(TypedDict):
    raw_texts: List[str]         # Input: Raw text of every paper
    paper_summaries: List[str]   # Internal: Structured summary of each paper
    final_report: str            # Output: Final markdown comparison

# --- IMPROVED Helper Function for Clean Extraction ---
def get_clean_content(llm_response):
    """
    CLEANUP FIX:
    Gemini 3.0 returns structured data like: 
    [{'type': 'text', 'text': 'Actual Content', 'extras': {...}}]
    
    This function digs inside that structure to extract ONLY the 'text' value,
    removing the dictionary brackets, type keys, and signatures.
    """
    content = llm_response.content

    # Case 1: It's already a simple string
    if isinstance(content, str):
        return content

    # Case 2: It's a list (common with Gemini 3)
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                # Extract 'text' key if it exists, otherwise skip
                text_parts.append(item.get('text', ''))
            else:
                # Fallback
                text_parts.append(str(item))
        return "\n".join(text_parts)

    # Case 3: It's a single dictionary
    if isinstance(content, dict):
        return content.get('text', str(content))
        
    return str(content)

# 2. Define Node: Summarize Individual Papers
def summarize_papers_node(state: ResearchState):
    """Takes raw texts and generates a structured summary for EACH paper individually."""
    raw_texts = state['raw_texts']
    summaries = []
    
    print(f"--- Node 1: Summarizing {len(raw_texts)} papers ---")
    
    for i, text in enumerate(raw_texts):
        # Snippet limit (Safeguard for speed)
        snippet = text[:50000] 
        
        prompt = (
            "You are a high-speed research analyst. Analyze this academic paper text. "
            "Extract the following strictly:\n"
            "1. Core Problem Addressed\n"
            "2. Methodology Used (specific algorithms/techniques)\n"
            "3. Key Quantitative Results (metrics, accuracy scores)\n"
            "4. Limitations & Future Work\n\n"
            f"TEXT CONTEXT:\n{snippet}"
        )
        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            # FIXED: Use the robust cleaner
            clean_summary = get_clean_content(response)
            summaries.append(clean_summary)
            print(f"   Paper {i+1} summarized.")
        except Exception as e:
            error_msg = f"Error summarizing paper: {e}"
            summaries.append(error_msg)
            print(f"   {error_msg}")
        
    return {"paper_summaries": summaries}

# 3. Define Node: Comparative Synthesis
def compare_papers_node(state: ResearchState):
    """Takes individual summaries and builds the cross-paper comparison."""
    summaries = state['paper_summaries']
    
    print("--- Node 2: Generating Comparison Report ---")
    
    # Combine summaries into one context block
    combined_context = ""
    for i, summ in enumerate(summaries):
        combined_context += f"\n--- PAPER {i+1} SUMMARY ---\n{summ}\n"
        
    prompt = (
        "You are an expert conducting a comparative literature review. "
        "I will provide summaries of multiple papers. "
        "Create a comprehensive Comparative Analysis in Markdown format.\n\n"
        "Output Structure Requirements:\n"
        "## 1. Executive Summary\n"
        "Briefly overview the common theme of these papers.\n\n"
        "## 2. Comparative Table\n"
        "Create a Markdown table comparing: Paper Title/ID, Problem, Method, Best Metric/Result.\n\n"
        "## 3. Deep Dive: Methodology\n"
        "Compare and contrast the approaches. How do they differ?\n\n"
        "## 4. Critical Analysis\n"
        "- What are the shared limitations?\n"
        "- Which paper presents the most robust solution?\n\n"
        f"INPUT DATA:\n{combined_context}"
    )
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        # FIXED: Use the robust cleaner to strip JSON artifacts
        return {"final_report": get_clean_content(response)}
    except Exception as e:
        return {"final_report": f"Error generating report: {e}"}

# 4. Build the Graph
builder = StateGraph(ResearchState)
builder.add_node("summarize_individual", summarize_papers_node)
builder.add_node("generate_comparison", compare_papers_node)

builder.set_entry_point("summarize_individual")
builder.add_edge("summarize_individual", "generate_comparison")
builder.add_edge("generate_comparison", END)

research_graph = builder.compile()

# ---------------- HELPER FUNCTIONS ----------------
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)[:60].strip()

def get_text_from_path(filepath):
    try:
        if filepath.lower().endswith('.pdf'):
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        elif filepath.lower().endswith('.docx'):
            doc = docx.Document(filepath)
            return "\n".join([p.text for p in doc.paragraphs])
        elif filepath.lower().endswith('.txt'):
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception as e:
        print(f"Extraction Error for {filepath}: {e}")
    return ""

# ---------------- ROUTES ----------------

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
    return send_from_directory(UPLOAD_FOLDER, filename)

# --- UPLOAD API ---
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

# --- SEARCH API ---
@app.route('/api/search', methods=['POST'])
def search_papers():
    data = request.json
    topic = data.get('topic')
    downloaded_results = []

    if not topic:
        return jsonify({"error": "No topic provided"}), 400

    headers = {"x-api-key": SEMANTIC_API_KEY}
    params = {"query": topic, "limit": 10, "fields": "title,year,authors,openAccessPdf,externalIds"}

    try:
        response = requests.get(SEMANTIC_BASE_URL, headers=headers, params=params)
        
        # Fallback if API key fails/missing
        if response.status_code in [401, 403]:
            response = requests.get(SEMANTIC_BASE_URL, params=params)

        api_data = response.json().get("data", [])
        
        count = 0
        for paper in api_data:
            if count >= 4: break 

            pdf_url = None
            if paper.get("openAccessPdf") and paper["openAccessPdf"].get("url"):
                pdf_url = paper["openAccessPdf"]["url"]
            elif paper.get("externalIds", {}).get("ArXiv"):
                pdf_url = f"https://arxiv.org/pdf/{paper['externalIds']['ArXiv']}.pdf"

            if pdf_url:
                try:
                    dl_headers = {"User-Agent": "Mozilla/5.0"}
                    pdf_res = requests.get(pdf_url, headers=dl_headers, timeout=10)
                    
                    if "application/pdf" in pdf_res.headers.get("Content-Type", "") or pdf_res.content[:4] == b'%PDF':
                        clean_title = sanitize_filename(paper['title'])
                        file_name = f"{clean_title}.pdf"
                        file_path = os.path.join(UPLOAD_FOLDER, file_name)
                        
                        with open(file_path, "wb") as f: 
                            f.write(pdf_res.content)
                        
                        authors = [a["name"] for a in paper.get("authors", [])][:2]
                        downloaded_results.append({
                            "id": paper["paperId"],
                            "title": paper["title"],
                            "filename": file_name,
                            "meta": f"{paper.get('year', 'N/A')} • {', '.join(authors)}",
                            "url": url_for('serve_file', filename=file_name)
                        })
                        count += 1
                except:
                    continue
        
        return jsonify({"status": "success", "papers": downloaded_results})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- ANALYSIS API ---
@app.route("/api/analyze", methods=["POST"])
def analyze_api():
    if not GEMINI_API_KEY:
         return jsonify({"status": "error", "message": "Server Config Error: API Key missing"})

    filenames = request.json.get("files", [])
    raw_texts = []
    
    # 1. Prepare Data
    for fname in filenames:
        path = os.path.join(UPLOAD_FOLDER, fname)
        if os.path.exists(path):
            text = get_text_from_path(path)
            if text.strip():
                raw_texts.append(text)

    if not raw_texts:
        return jsonify({"status": "error", "message": "No text content found in selected files."})

    try:
        # 2. Invoke LangGraph
        print(f"Starting Analysis with Gemini 3 Flash on {len(raw_texts)} files...")
        initial_state = {"raw_texts": raw_texts, "paper_summaries": [], "final_report": ""}
        result_state = research_graph.invoke(initial_state)
        
        # 3. Process Output
        final_markdown = result_state['final_report']

        # Extra safety: Ensure it is a string before markdown conversion
        # The 'get_clean_content' function should have already handled the dicts,
        # but this is a final fallback.
        if not isinstance(final_markdown, str):
            final_markdown = str(final_markdown)

        html_output = markdown.markdown(
            final_markdown, 
            extensions=['extra', 'tables', 'fenced_code', 'nl2br']
        )

        return jsonify({
            "status": "success",
            "html_content": html_output
        })

    except Exception as e:
        print(f"Graph Execution Error: {e}")
        return jsonify({"status": "error", "message": f"Analysis failed: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)