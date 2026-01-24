### Milestone 1 — Paper Collection & Dataset Preparation (Week 1–2)

---

## 📌 Project Overview

The **AI Research Paper Reviewer** is an automated system designed to support systematic literature reviews by simplifying the process of collecting and organizing academic research papers.

This project automates the early research workflow — from topic-based paper search to dataset preparation — enabling faster and more structured review creation.

---

## 🎯 Current Milestone: Week 1–2

**Goal:**  
Automate research paper discovery and prepare a clean dataset for further analysis.

---

## ✅ Features Implemented

- 🔍 Topic-based academic paper search  
- 🌐 Integration with **Semantic Scholar API**  
- 📄 Retrieval of paper metadata (title, authors, year, abstract)  
- 📥 Automatic PDF download (when available)  
- 🗂 Structured dataset generation in JSON format  
- 📁 Clean and modular project structure  

---

## 🧠 Workflow Implemented

User Topic Input
↓
Semantic Scholar API Search
↓
Research Paper Metadata Collection
↓
Top-N Paper Selection
↓
PDF Download
↓
Dataset Preparation


---

## 🧱 Project Structure

AI-System-to-automatically-Review-and-Summarize-Research-Papers/
│
├── data/
│ ├── papers/ # Downloaded research PDFs
│ ├── metadata/
│ │ └── papers_metadata.json # Research paper metadata
│ └── dataset.json # Final prepared dataset
│
├── src/
│ ├── init.py
│ ├── config.py # API keys and settings
│ ├── paper_search.py # Semantic Scholar search logic
│ └── utils.py # Helper utility functions
│
├── .gitignore
├── requirements.txt
└── README.md


---

## ⚙️ Technology Stack

- **Language:** Python 3.x  
- **API:** Semantic Scholar API  
- **Libraries:**
  - requests
  - json
  - pathlib
  - tqdm
  - python-dotenv (optional)

---

## 🔧 Setup Instructions

### 1️⃣ Install Python 3.8+

Check Python version:

python --version


---

### 2️⃣ Clone the Repository

git clone https://github.com/springboardmentor50641l/AI-System-to-automatically-Review-and-Summarize-Research-Papers.git
cd AI-System-to-automatically-Review-and-Summarize-Research-Papers


---

### 3️⃣ Create Virtual Environment (Recommended)

python -m venv venv


Activate environment:

**Windows**
venv\Scripts\activate


**macOS / Linux**
source venv/bin/activate


---

### 4️⃣ Install Dependencies

pip install -r requirements.txt


---

### 5️⃣ Configure API Key

Edit the file:

src/config.py


Add your Semantic Scholar API key:

```python
SEMANTIC_SCHOLAR_API_KEY = "your_api_key_here"
⚠️ Do not upload API keys to GitHub.

▶️ How to Run
python src/paper_search.py
📤 Generated Outputs
File	Description
papers_metadata.json	Metadata of collected papers
dataset.json	Structured dataset for analysis
/papers/	Downloaded research PDFs
📊 Sample Dataset Format
{
  "paper_id": "123456",
  "title": "Artificial Intelligence in Healthcare",
  "authors": ["Author A", "Author B"],
  "year": 2023,
  "abstract": "...",
  "pdf_url": "...",
  "local_pdf_path": "data/papers/ai_healthcare.pdf"
}
✅ Milestone 1 Achievements
✔ Environment setup completed
✔ Semantic Scholar API integrated
✔ Automated research paper search
✔ PDF download pipeline implemented
✔ Dataset generation completed
✔ Code structured for scalability

🔜 Upcoming Milestone (Week 3–4)
PDF text extraction

Section-wise content segmentation

Key finding identification

Cross-paper comparison module

👩‍🏫 Internship Context
This project is developed as part of the
Infosys Springboard Internship Program
under guided milestone-based evaluation.

📜 License
For academic and educational use only.

⭐ Milestone 1 successfully completed.



