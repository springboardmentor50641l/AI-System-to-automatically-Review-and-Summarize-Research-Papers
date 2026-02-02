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


# def run_pipeline(topic, mode):
#     texts = []
#     papers = []

#     # ================= AUTOMATIC MODE =================
#     if mode == "automatic":
#         plan_research(topic)
#         papers = search_papers(topic, MAX_PAPERS)

#         for i, p in enumerate(papers):
#             pdf_info = p.get("openAccessPdf")

#             if not pdf_info or not pdf_info.get("url"):
#                 continue

#             path = download_pdf(pdf_info["url"], f"paper_{i}")

#             if path:
#                 text = extract_text(path)
#                 if text.strip():
#                     texts.append(text)

#     # ================= MANUAL MODE =================
#     else:
#         if not os.path.exists(PAPER_DIR):
#             return "Paper directory not found."

#         for f in os.listdir(PAPER_DIR):
#             if f.lower().endswith(".pdf"):
#                 path = os.path.join(PAPER_DIR, f)
#                 text = extract_text(path)
#                 if text.strip():
#                     texts.append(text)

#     # ================= VALIDATION =================
#     if len(texts) == 0:
#         return "No valid research papers found for analysis."

#     # ================= ANALYSIS =================
#     analysis = analyze_papers(texts[:3])

#     # ================= WRITING =================
#     draft = generate_draft(analysis)

#     # ================= REVIEW =================
#     final = review_paper(draft)

#     # ================= REFERENCES =================
#     refs = format_references(papers)

#     # ================= SAVE OUTPUT =================
#     os.makedirs(OUTPUT_DIR, exist_ok=True)
#     filename = f"summary_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
#     output_path = os.path.join(OUTPUT_DIR, filename)

#     with open(output_path, "w", encoding="utf-8") as f:
#         f.write(final)
#         f.write("\n\nREFERENCES\n")
#         f.write(refs)

#     return final

# ----------------------------------------------------------------------------------------------------------------------- #
# new code with llm
import os
import datetime

from config import PAPER_DIR, OUTPUT_DIR, MAX_PAPERS
from modules.planner import plan_research
from modules.paper_retrieval import search_papers
from modules.pdf_downloader import download_pdf
from modules.text_extractor import extract_text
from modules.analyzer import analyze_papers
from modules.draft_generator import generate_draft
from modules.reviewer import review_paper
from utils.apa_formatter import format_references


def run_pipeline(topic: str, mode: str) -> str:
    """
    Orchestrates the complete AI-based research paper review pipeline.
    Supports both automatic (Semantic Scholar) and manual (local PDF) modes.
    """

    texts = []
    papers = []

    # ================= AUTOMATIC MODE =================
    if mode == "automatic":
        plan_research(topic)
        papers = search_papers(topic, MAX_PAPERS)

        for i, paper in enumerate(papers):
            pdf_info = paper.get("openAccessPdf")

            # Skip papers without open-access PDFs
            if not pdf_info or not pdf_info.get("url"):
                continue

            pdf_path = download_pdf(pdf_info["url"], f"paper_{i}")

            if pdf_path:
                text = extract_text(pdf_path)
                if text and text.strip():
                    texts.append(text)

    # ================= MANUAL MODE =================
    else:
        if not os.path.exists(PAPER_DIR):
            return "❌ Paper directory not found. Please add PDFs to the papers folder."

        for file in os.listdir(PAPER_DIR):
            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(PAPER_DIR, file)
                text = extract_text(pdf_path)

                if text and text.strip():
                    texts.append(text)

    # ================= VALIDATION =================
    if len(texts) < 2:
        return "❌ At least two valid research papers are required for comparison."

    # ================= ANALYSIS =================
    analysis = analyze_papers(texts[:3])  # Compare up to 3 papers

    # ================= DRAFT GENERATION =================
    draft = generate_draft(analysis)

    # ================= REVIEW & REFINEMENT =================
    final_output = review_paper(draft)

    # ================= REFERENCES =================
    references = format_references(papers)

    # ================= SAVE OUTPUT =================
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"summary_{timestamp}.txt"
    output_path = os.path.join(OUTPUT_DIR, output_file)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"RESEARCH TOPIC: {topic}\n")
        f.write(f"INPUT MODE: {mode.upper()}\n")
        f.write(f"GENERATED ON: {datetime.datetime.now()}\n\n")
        f.write(final_output)
        f.write("\n\nREFERENCES\n")
        f.write(references)

    return final_output

