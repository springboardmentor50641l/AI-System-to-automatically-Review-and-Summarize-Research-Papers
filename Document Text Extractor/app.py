import os
from flask import Flask, render_template, request, send_from_directory
from PyPDF2 import PdfReader
import docx

app = Flask(__name__)

# ---------------- CONFIGURATION ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "extracted_text")

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

# ---------------- HELPER FUNCTIONS ----------------

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(filepath, extension):
    """Router for extraction based on extension"""
    try:
        if extension == "pdf":
            reader = PdfReader(filepath)
            return "".join([page.extract_text() or "" for page in reader.pages])
        
        elif extension == "docx":
            doc = docx.Document(filepath)
            return "\n".join([p.text for p in doc.paragraphs])
        
        elif extension == "txt":
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception as e:
        return f"Error during extraction: {str(e)}"

# ---------------- MAIN ROUTE ----------------

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    
    if request.method == "POST":
        file = request.files.get("file")

        # 1. Validation
        if not file or file.filename == "":
            message = "❌ No file selected"
            return render_template("index.html", message=message)

        if not allowed_file(file.filename):
            message = "❌ Unsupported format. Use PDF, DOCX, or TXT."
            return render_template("index.html", message=message)

        # 2. Save Original File
        filename = file.filename
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # 3. Process Extraction
        ext = filename.rsplit(".", 1)[1].lower()
        extracted_text = extract_text(filepath, ext)

        # 4. Save Extracted Result
        output_filename = f"{filename}_extracted.txt"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)

        message = f"✅ Success! Text extracted from {filename}."
        
        # Optional: You can pass the extracted text back to the UI
        # return render_template("index.html", message=message, content=extracted_text)

    return render_template("index.html", message=message)

# Route to download the result if needed
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)