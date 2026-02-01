# 📄 AI Research Paper Analysis System

![Project Status](https://img.shields.io/badge/Status-Active-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Flask](https://img.shields.io/badge/Framework-Flask-orange)

An AI-powered web application that allows users to upload research papers, extract text, analyze content, and perform intelligent queries using Natural Language Processing (NLP) techniques.

---

## 🚀 Project Overview

This project is designed to simplify research paper analysis by enabling users to:
* Upload academic research papers (PDF/text-based).
* Automatically extract and store text.
* Analyze research content efficiently.
* Query papers using natural language.
* View structured insights through a web interface.

It is especially useful for **Data Science**, **AI**, and **Research-oriented** domains.

---

## 🧠 Key Features

* **📤 Upload System:** Seamless interface to upload research papers.
* **📄 Text Extraction:** Automatically extracts text from PDFs and stores them.
* **🔍 NLP Analysis:** Performs content analysis using Natural Language Processing.
* **💬 Query Interface:** Ask questions related to the extracted papers.
* **🌐 Responsive UI:** Clean web interface using Flask, HTML, CSS, and JS.
* **📁 Organized Storage:** Structured file system for extracted text management.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Python, Flask |
| **Frontend** | HTML, CSS, JavaScript |
| **NLP** | Python NLP Libraries |
| **Styling** | Custom CSS |
| **Environment** | Python Virtual Environment |

---

## 📂 Project Directory Structure

```text
Final Project/
│
├── app.py                     # Main Flask application
├── requirements.txt           # Project dependencies
├── .env                       # Environment variables
├── README.md                  # Project documentation
│
├── papers/                    # Uploaded research papers
│
├── extracted_text/            # Extracted text from papers
│   ├── *.txt
│
├── static/
│   ├── css/
│   │   └── style.css          # UI styling
│   ├── js/
│   │   └── script.js          # Frontend logic
│   └── images/
│
├── templates/
│   ├── index.html             # Home page
│   ├── analysis.html          # Analysis results page
│   └── query.html             # Query interface

```

---

## ⚙️ Prerequisites

Before running the project, ensure you have the following installed:

1. **Python 3.8** or above.
2. **pip** (Python package manager).
3. Basic knowledge of Flask (helpful but not required).

---

## 📦 Installation & Setup

Follow these steps to set up the project locally.

### 🔹 Step 1: Clone or Extract the Project

Clone the repository or extract the ZIP file.

```bash
# If using git
git clone <repository-url>

# If using downloaded ZIP, navigate to the folder:
cd "Final Project/Final Project"

```

### 🔹 Step 2: Create Virtual Environment (Recommended)

It is best practice to run this project in a virtual environment.

```bash
# Create the environment
python -m venv venv

```

**Activate the environment:**

* **Windows:**
```bash
venv\Scripts\activate

```


* **Linux / Mac:**
```bash
source venv/bin/activate

```



### 🔹 Step 3: Install Dependencies

Install the required Python packages.

```bash
pip install -r requirements.txt

```

### 🔹 Step 4: Configure Environment Variables

Open or create a `.env` file in the root directory and add the following:

```ini
FLASK_ENV=development
FLASK_DEBUG=True

```

---

## ▶️ Execution Steps

### 🔹 Step 5: Start Flask Server

Run the main application file.

```bash
python app.py

```

### 🔹 Step 6: Access the Application

Open your web browser and visit:

```
[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

```

---

## 🔄 Application Workflow

1. **Home Page:** User uploads a research paper.
2. **Text Extraction:** The system processes the file, extracts text, and saves it to `extracted_text/`.
3. **Analysis Page:** AI processes the text to generate insights.
4. **Query Page:** User asks natural language questions about the paper.
5. **Results:** Relevant answers and data are displayed.

---

## 🧪 Sample Extracted Output

Extracted papers are stored as `.txt` files in the directory below. Each file corresponds to one uploaded research paper.

```text
extracted_text/

```

---

## 🛡️ Error Handling

* **Invalid Files:** Non-compatible files are rejected.
* **Validation:** Server-side validations ensure data integrity.
* **UI Feedback:** Graceful error messages are displayed to the user.

---

## 📈 Future Enhancements

* [ ] PDF Syntax Highlighting.
* [ ] Advanced Research Paper Summarization.
* [ ] Model-based Recommendations.
* [ ] User Authentication & History.
* [ ] Cloud Deployment (AWS/Heroku).

---

## 👨‍💻 Author

**Pranjal Upadhyay**

* *B.Tech CSE (AI & Data Science)*
* *Aspiring Data Scientist & AI Engineer*
