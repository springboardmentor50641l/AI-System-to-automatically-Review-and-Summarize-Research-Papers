import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from graph.llm_config import llm

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from search import search_papers
from download import select_and_download_pdfs
from dataset import prepare_dataset

from graph.pipeline import (
    build_extraction_pipeline,
    build_review_pipeline
)


def sanitize_topic(topic: str) -> str:
    return topic.lower().replace(" ", "_")


def main():
    load_dotenv()

    api_key = os.getenv("CORE_API_KEY")
    if not api_key:
        raise RuntimeError("CORE_API_KEY not found")

    topic = input("Enter research topic: ").strip()
    safe_topic = sanitize_topic(topic)
    paper_folder = os.path.join("papers", safe_topic)

    print("Searching research papers...")
    papers = search_papers(topic, api_key)

    print("Downloading PDFs...")
    downloaded_papers, _ = select_and_download_pdfs(
    papers,
    required_count=3,
    folder=paper_folder
    )


    if not downloaded_papers:
        print("No PDFs downloaded. Cannot generate review.")
        return


    print("Processing papers...")
    extraction_pipeline = build_extraction_pipeline()

    for pdf_path in downloaded_papers:
        extraction_pipeline.invoke({"pdf_path": pdf_path})

    print("Preparing dataset...")
    df = prepare_dataset(downloaded_papers, folder=paper_folder)
    df.to_csv("research_dataset.csv", index=False)

    print("Generating literature review...")
    review_pipeline = build_review_pipeline()

    final_state = review_pipeline.invoke({})
    final_review = final_state.get("final_review", "")

    review_path = os.path.join(paper_folder, "final_literature_review.txt")
    with open(review_path, "w", encoding="utf-8") as f:
        f.write(final_review)

    print("FINAL REVIEW SAVED:", review_path)




if __name__ == "__main__":
    main()
