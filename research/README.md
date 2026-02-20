# Automated Research Paper Review System (Semantic Scholar + Gemini + LangGraph)

This project is an automated research paper pipeline that searches for research papers, downloads PDFs, extracts text, semantically sections each paper into a standardized structure using Gemini, and finally generates key findings, cross-paper comparison, and a draft literature review.

---

## ✅ Project Features Completed (So Far)

### 1. Environment Setup
- Project environment configured using `pyproject.toml`
- Dependencies managed using both `pyproject.toml` and `requirement.txt`

### 2. Automated Paper Search
- Paper search implemented using Semantic Scholar API
- The system accepts a research topic and retrieves relevant papers programmatically

### 3. Paper Selection and PDF Download
- Downloads open-access PDFs automatically
- Stores papers in topic-based folders:

- Saves metadata in JSON format (`metadata.json`)

### 4. Dataset Preparation (Structured Dataset)
- Extracts paper text
- Converts unstructured PDF text into standardized structured sections
- Stores each paper as JSON sections for downstream analysis

### 5. Automated Semantic Text Extraction and Sectioning (LLM-Based)
- Extracts full text from PDF using PyMuPDF
- Normalizes extracted text
- Uses Gemini to semantically section papers into:
- abstract
- introduction
- background_work
- proposed_solution
- methodology
- results
- discussion
- conclusion
- references

### 6. Key Finding Extraction and Cross-Paper Comparison
- Extracts key findings for each paper using Gemini
- Compares multiple papers and generates:
- strengths
- limitations
- differences in methodology and results
- Generates a draft literature review

---

---

## ⚙️ Requirements

- Python 3.11+
- Internet access (for Semantic Scholar and Gemini API)

---

## 📦 Key Dependencies

- `google-genai` (Gemini API client)
- `langgraph` (workflow orchestration)
- `pandas` (data processing)
- `pymupdf` (PDF text extraction)
- `python-dotenv` (environment variable management)

---

## 🔑 Environment Variables (.env)

Create a `.env` file in the root folder.

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_key   # optional


🚀 Quick Start
1. Install dependencies
pip install -r requirement.txt

2. Run the pipeline
python rull_all.py "machine learning" --limit 10
streamlit run app.py 
