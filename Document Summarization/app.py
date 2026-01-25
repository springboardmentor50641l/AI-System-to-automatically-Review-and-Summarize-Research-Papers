import os
import markdown
from flask import Flask, render_template, request
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PyPDF2 import PdfReader
import docx

# 1. Load Environment Variables (.env)
load_dotenv()

app = Flask(__name__)

# 2. Configure Gemini Client
# Using the 2026 stable client and model
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_ID = "gemini-3-flash-preview"

# 3. Extraction Logic
def get_text_from_file(file):
    """Router to handle different file types and return plain text."""
    filename = file.filename.lower()
    try:
        if filename.endswith('.pdf'):
            reader = PdfReader(file)
            return " ".join([page.extract_text() or "" for page in reader.pages])
        elif filename.endswith('.docx'):
            doc = docx.Document(file)
            return "\n".join([p.text for p in doc.paragraphs])
        elif filename.endswith('.txt'):
            return file.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Extraction Error: {e}")
        return ""

# 4. Main Route
@app.route("/", methods=["GET", "POST"])
def index():
    summary_html = None
    
    if request.method == "POST":
        file = request.files.get('file')
        
        if file and file.filename != "":
            # A. Extract the text from the uploaded file
            raw_text = get_text_from_file(file)
            
            if raw_text.strip():
                try:
                    # B. Define the System Instruction for Structure
                    # This ensures the AI uses the H1, H2, and Bold tags your CSS expects
                    instruction = (
                        "You are a Research Assistant. Summarize the provided document into a structured report. "
                        "Use an H1 title for the top heading. Use H2 for main sections like 'Overview', 'Methodology', "
                        "and 'Key Findings'. Use bullet points for details and bold key technical terms."
                    )

                    # C. Generate Content
                    # Using the modern 'generate_content' with system_config
                    response = client.models.generate_content(
                        model=MODEL_ID,
                        contents=f"Please analyze and summarize this text: \n\n {raw_text[:30000]}",
                        config=types.GenerateContentConfig(
                            system_instruction=instruction,
                            temperature=0.7
                        )
                    )

                    # D. Convert Markdown to HTML
                    # This allows the '{{ summary | safe }}' in your HTML to render properly
                    if response.text:
                        summary_html = markdown.markdown(
                            response.text, 
                            extensions=['extra', 'tables', 'fenced_code']
                        )
                except Exception as e:
                    summary_html = f"<p style='color:red;'>AI Error: {str(e)}</p>"
            else:
                summary_html = "<p style='color:orange;'>Could not read file content.</p>"

    return render_template("index.html", summary=summary_html)

if __name__ == "__main__":
    # Ensure local 'uploads' directory doesn't cause issues
    app.run(debug=True, port=5000)