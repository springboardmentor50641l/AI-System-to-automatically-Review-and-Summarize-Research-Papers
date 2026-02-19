# 📄 AI Research Paper Analysis System (Powered by LangGraph)

![Project Status](https://img.shields.io/badge/Status-Active-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-purple) ![Gemini](https://img.shields.io/badge/AI-Gemini%203.0-blueviolet)

An AI-powered web application that orchestrates advanced research paper analysis using **LangGraph** and **Google Gemini 3.0**. It allows users to search for papers via Semantic Scholar, upload documents, and generate deep comparative reports through a multi-step agentic workflow.

---

## 🚀 Project Overview

This project evolves traditional document analysis by using **Graph-based AI workflows**. Instead of simple text summarization, it employs a **LangGraph StateGraph** to:
1.  **Search & Acquire:** Fetch relevant academic papers automatically.
2.  **Individual Analysis:** Summarize each paper independently to extract methodology and metrics.
3.  **Comparative Synthesis:** aggregate insights to produce a structured comparative literature review.

It is designed for **Data Scientists**, **Researchers**, and **Students** who need to synthesize multiple papers quickly.

---

## 🧠 Key Features

* **🤖 LangGraph Orchestration:** Uses a stateful graph to manage the workflow between individual paper summarization and final comparative reporting.
* **🌍 Automated Paper Search:** Integrated with the **Semantic Scholar API** to search and download open-access PDFs directly.
* **📤 Smart Upload System:** Supports PDF, DOCX, and text file uploads.
* **🔍 Deep Extraction:** Extracts core problems, methodologies, quantitative results, and limitations.
* **📊 Comparative Reports:** Generates Markdown-formatted tables comparing multiple papers side-by-side.
* **💬 Natural Language Query:** (Coming Soon) Ask specific questions across the document set.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Orchestration** | **LangGraph**, LangChain |
| **LLM Engine** | **Google Gemini 3.0 Flash** |
| **Backend** | Python, Flask |
| **External APIs** | **Semantic Scholar API** |
| **Frontend** | HTML, CSS, JavaScript |
| **Processing** | PyPDF2, python-docx |

---

## 📂 Project Directory Structure

```text
Final Project/
│
├── app.py                     # Main Flask app with LangGraph workflow
├── requirements.txt           # Project dependencies
├── .env                       # API Keys (Gemini & Semantic Scholar)
├── README.md                  # Project documentation
│
├── papers/                    # Storage for uploaded/downloaded PDFs
│
├── templates/
│   ├── index.html             # Home & Upload
│   ├── analysis.html          # Results visualization
│   ├── query.html             # Chat interface
|   └── login.html             # Login and Signup
│
└── static/
    ├── css/style.css
    └── js/script.js

```

---

## ⚙️ Prerequisites

Before running the project, ensure you have:

1. **Python 3.9+** (Recommended for modern LangChain/LangGraph support).
2. **Google Cloud API Key** (Access to Gemini models).
3. **Semantic Scholar API Key** (Optional, but recommended for higher rate limits).

---

## 📦 Installation & Setup

### 🔹 Step 1: Clone the Repository

```bash
git clone <repository-url>
cd "Final Project"

```

### 🔹 Step 2: Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate

```

### 🔹 Step 3: Install Dependencies

```bash
pip install -r requirements.txt

```

### 🔹 Step 4: Configure Environment Variables

Create a `.env` file in the root directory and add your keys:

```ini
# Required for Analysis
GEMINI_API_KEY=your_google_gemini_key_here

# Optional (for better Paper Search limits)
SEMANTIC_API_KEY=your_semantic_scholar_key_here

FLASK_DEBUG=True

```

---

## ▶️ Execution Steps

### 🔹 Step 5: Start the Application

```bash
python app.py

```

### 🔹 Step 6: Access the Interface

Open your browser and visit: `http://127.0.0.1:5000/`

---

## 🔄 LangGraph Workflow Architecture

The application uses a **StateGraph** to ensure high-quality output. The workflow follows these nodes:

1. **Input State:** Raw text is loaded from multiple PDF/DOCX files.
2. **Node 1: Summarize (`summarize_individual`)**:
* The LLM iterates through every paper individually.
* It extracts strict structured data (Problem, Method, Metrics).
* *Self-Correction:* Includes JSON cleaning logic to handle Gemini 3.0 outputs.


3. **Node 2: Synthesize (`generate_comparison`)**:
* The graph passes the structured summaries to a second LLM call.
* The model generates a "Comparative Analysis" including an Executive Summary and Comparison Table.


4. **Output:** A rendered HTML report.

---

## 🛡️ Error Handling

* **API Failures:** Graceful fallback if Semantic Scholar is down or API keys are invalid.
* **Content Cleaning:** Custom regex logic (`get_clean_content`) ensures clean Markdown output even if the model returns raw JSON.
* **File Parsing:** Robust handling for encrypted PDFs or corrupted files.

---

## 👨‍💻 Author

**Pranjal Upadhyay**

* *B.Tech CSE (AI & Data Science)*
* *Aspiring Data Scientist & AI Engineer*
