# AI-System-to-automatically-Review-and-Summarize-Research-Papers

This project automates the process of generating structured academic research reviews.  
It covers the complete workflow from paper retrieval to structured synthesis and refinement using a modular, graph-based architecture.

---

## Overview

The system performs:

- Research paper search using Semantic Scholar API  
- PDF download and metadata storage  
- Text extraction and normalization  
- Semantic sectioning using Gemini (LLM-based)  
- Key findings extraction  
- Cross-paper comparison  
- Structured review generation (Abstract, Methods, Results, APA References)  
- Critique and revision cycle  
- Interactive Gradio user interface  

---

## Project Structure

```text
AI-System/
│
├── app.py
├── requirements.txt
├── .env
│
├── scripts/
│   ├── semantic_search.py
│   └── download_papers.py
│
├── pipeline/
│   ├── graph.py
│   ├── run_graph.py
│   ├── state.py
│   │
│   ├── core/
│   │   ├── extract.py
│   │   ├── normalize.py
│   │   └── section.py
│   │
│   ├── nodes/
│   │   ├── extract_node.py
│   │   ├── normalize_node.py
│   │   └── section_node.py
│   │
│   └── analysis/
│       ├── paper_analysis.py
│       ├── run_analysis.py
│       ├── structured_writer.py
│       └── review_module.py
│
├── data/
│   ├── raw_papers/
│   ├── sections/
│   ├── metadata/
│   └── analysis_outputs/
│
└── docs/
```



Note: The `data/` directory stores generated outputs and may not be fully tracked in Git.

---

## Installation

1. Clone the repository

git clone <repository_url>
cd AI-System


2. Create and activate virtual environment

python -m venv venv
venv\Scripts\activate


3. Install dependencies

pip install -r requirements.txt


4. Create a `.env` file in the root directory

GEMINI_API_KEY=your_gemini_api_key
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_api_key


---

## Running the Application

Start the Gradio interface:
python app.py

Open the local URL shown in the terminal.

Enter a research topic and run the full pipeline.

If a topic has already been processed, the system automatically reuses:

- Existing metadata  
- Previously downloaded PDFs  
- Section JSON files  
- Analytical drafts  
- Structured reviews  

This prevents duplicate processing and unnecessary API calls.

---

## Technologies Used

- Python  
- PyMuPDF  
- LangGraph  
- LangChain + Gemini API  
- Semantic Scholar API  
- Gradio  

---

## Output

Generated outputs are stored in:
data/analysis_outputs/


Including:

- Analytical drafts  
- Final structured review  
- Critique output  
- Revised review  

---

## Author

Manohar Jatla  
