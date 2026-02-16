
# # new code with llm
# import os
# import datetime

# from config import PAPER_DIR, OUTPUT_DIR, MAX_PAPERS
# from modules.planner import plan_research
# from modules.paper_retrieval import search_papers
# from modules.pdf_downloader import download_pdf
# from modules.text_extractor import extract_text
# from modules.analyzer import analyze_papers
# from modules.draft_generator import generate_draft
# from modules.reviewer import review_paper
# from utils.apa_formatter import format_references
# from utils.pdf_writer import save_text_as_pdf


# def run_pipeline(topic: str, mode: str) -> str:
#     """
#     Orchestrates the complete AI-based research paper review pipeline.
#     Supports both automatic (Semantic Scholar) and manual (local PDF) modes.
#     """

#     texts = []
#     papers = []

#     # ================= AUTOMATIC MODE =================
#     if mode == "automatic":
#         plan_research(topic)
#         papers = search_papers(topic, MAX_PAPERS)

#         for i, paper in enumerate(papers):
#             pdf_info = paper.get("openAccessPdf")

#             if not pdf_info or not pdf_info.get("url"):
#                 continue

#             pdf_path = download_pdf(pdf_info["url"], f"paper_{i}")

#             if pdf_path:
#                 text = extract_text(pdf_path)
#                 if text and text.strip():
#                     texts.append(text)

#     # ================= MANUAL MODE =================
#     else:
#         if not os.path.exists(PAPER_DIR):
#             return "Paper directory not found. Please add PDFs to the papers folder."

#         for file in os.listdir(PAPER_DIR):
#             if file.lower().endswith(".pdf"):
#                 pdf_path = os.path.join(PAPER_DIR, file)
#                 text = extract_text(pdf_path)

#                 if text and text.strip():
#                     texts.append(text)

#     # ================= VALIDATION =================
#     if len(texts) < 2:
#         return "At least two valid research papers are required for comparison."

#     # ================= ANALYSIS =================
#     analysis = analyze_papers(texts[:3])

#     # ================= DRAFT GENERATION =================
#     draft = generate_draft(analysis, topic, mode)

#     # ================= REVIEW =================
#     final_output = review_paper(draft)

#     # Ensure string output
#     if isinstance(final_output, list):
#         final_output = "\n\n".join(final_output)

#     # ================= REFERENCES =================
#     if papers:
#         references = format_references(papers)
#     else:
#         references = "Manual mode: Reference metadata not available."

#     # ================= SAVE OUTPUT =================
#     os.makedirs(OUTPUT_DIR, exist_ok=True)

#     timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     txt_path = os.path.join(OUTPUT_DIR, f"summary_{timestamp}.txt")
#     pdf_path = os.path.join(OUTPUT_DIR, f"summary_{timestamp}.pdf")

#     full_text = final_output + "\n\nREFERENCES\n" + references

#     with open(txt_path, "w", encoding="utf-8") as f:
#         f.write(full_text)

#     save_text_as_pdf(full_text, pdf_path)

#     return final_output

#-------------------------------------------------------------------------------#

import os

from config import PAPER_DIR, MAX_PAPERS
from modules.planner import plan_research
from modules.paper_retrieval import search_papers
from modules.pdf_downloader import download_pdf
from modules.text_extractor import extract_text
from utils.apa_formatter import format_references

# Import Workflow Controller
from graph.workflow import run_workflow


def run_pipeline(topic: str, mode: str, uploaded_files=None) -> str:
    """
    Main Pipeline Controller.
    Handles paper retrieval and delegates analysis to workflow.
    Returns final formatted output (NO AUTO SAVE).
    """

    texts = []
    papers = []

    # ================= AUTOMATIC MODE =================
    if mode == "automatic":

        plan_research(topic)
        papers = search_papers(topic, MAX_PAPERS)

        for i, paper in enumerate(papers):

            pdf_info = paper.get("openAccessPdf")

            if not pdf_info or not pdf_info.get("url"):
                continue

            pdf_path = download_pdf(pdf_info["url"], f"paper_{i}")

            if pdf_path:
                text = extract_text(pdf_path)
                if text and text.strip():
                    texts.append(text)

    # ================= MANUAL MODE =================
    else:
        if not uploaded_files or len(uploaded_files) < 2:
            return "Please upload at least two PDF files for manual mode."

        for file in uploaded_files:
            try:
                pdf_path = file.name
                text = extract_text(pdf_path)

                if text and text.strip():
                    texts.append(text)

            except Exception as e:
                print(f"[Manual Mode Error] {e}")

    # ================= VALIDATION =================
    if len(texts) < 2:
        return "At least two valid research papers are required for comparison."

    # ================= WORKFLOW EXECUTION =================
    try:
        final_output = run_workflow(texts[:3], topic, mode)
    except Exception as e:
        return f"Workflow execution failed: {str(e)}"

    # ================= REFERENCES =================
    if papers:
        references = format_references(papers)
    else:
        references = "Manual mode: Reference metadata not available."

    # ================= RETURN FINAL TEXT =================
    full_text = final_output + "\n\nREFERENCES\n" + references

    return full_text
