# AI Research Reviewer

An end to end AI powered system that automates research paper discovery, analysis, and structured review generation.

Built during the Infosys Internship Program to simplify literature review workflows for students, researchers, and developers.

---

## Project Vision

Manual literature reviews are time consuming and repetitive. This project demonstrates how modern AI and LLM pipelines can automate the entire research review lifecycle, from paper discovery to final draft generation.

The goal is to create a scalable research assistant that helps users quickly understand trends, compare findings, and produce structured review drafts.

---

## Key Capabilities

- Automated research paper retrieval using Semantic Scholar  
- Intelligent PDF download and text extraction  
- Content cleaning and normalization pipeline  
- LLM driven semantic section detection  
- Cross paper comparative analysis  
- Structured literature review draft generation  
- Interactive Gradio based user interface  

---

## System Workflow

1. User enters a research topic  
2. System fetches relevant papers via Semantic Scholar API  
3. PDFs are downloaded and parsed  
4. Extracted text is cleaned and normalized  
5. LLM performs semantic sectioning and understanding  
6. Cross paper insights are generated  
7. A structured review draft is produced  
8. Results are displayed in an interactive UI  

---

## Project Structure

Ai-Research-Reviewer/
│
├── Documents/ # Generated outputs and reports
├── data/ # Cached papers and intermediate data
├── modules/
│ ├── paper_search.py # Fetch papers from Semantic Scholar
│ ├── pdf_downloader.py # Download research PDFs
│ ├── text_extractor.py # Extract and clean text
│ ├── analyzer.py # Semantic analysis and insights
│ ├── draft_generator.py # Generate structured reviews
│ ├── reviewer.py # Review refinement logic
│
├── utils/ # Helper utilities
├── app.py # Gradio interface entry point
├── config.py # API keys and configuration
└── requirements.txt # Dependencies


---

## Tech Stack

### Core Technologies
- Python  
- Gradio  
- PyMuPDF  

### AI and APIs
- Semantic Scholar API  
- Google Gemini API  

---

## Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Ai-Research-Reviewer.git
cd Ai-Research-Reviewer
