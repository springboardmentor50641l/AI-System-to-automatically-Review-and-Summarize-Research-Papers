import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from search import search_papers
from download import select_and_download_pdfs
from dataset import prepare_dataset


def sanitize_topic(topic: str) -> str:
    """Convert topic into a safe folder name."""
    return topic.lower().replace(" ", "_")


def main():
    load_dotenv()

    api_key = os.getenv("CORE_API_KEY")
    if not api_key:
        raise RuntimeError("CORE_API_KEY not found in .env file")

    topic = input("Enter research topic: ").strip()
    if not topic:
        print("Topic cannot be empty")
        return

    safe_topic = sanitize_topic(topic)
    paper_folder = os.path.join("papers", safe_topic)

    print("Searching research papers...")
    papers = search_papers(topic, api_key, limit=50)

    if not papers:
        print("The data source is temporarily unable to process broad topics.")
        print("No papers returned by the API. Try a different topic.")
        return

    print("Downloading PDFs...")
    downloaded_papers, _ = select_and_download_pdfs(
        papers,
        required_count=3,
        folder=paper_folder
    )

    print("Preparing dataset...")
    df = prepare_dataset(
        downloaded_papers,
        folder=paper_folder,
        expected_count=3
    )

    csv_path = "research_dataset.csv"

    if os.path.exists(csv_path):
        df.to_csv(csv_path, mode="a", header=False, index=False)
    else:
        df.to_csv(csv_path, index=False)

    print("Completed successfully")
    print(f"Topic: {topic}")
    print(f"Papers with PDF: {len(downloaded_papers)} / 3")
    print("See research_dataset.csv for details")


if __name__ == "__main__":
    main()
