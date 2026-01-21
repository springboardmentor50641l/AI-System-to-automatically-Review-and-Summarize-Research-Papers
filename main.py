import sys
import os
from dotenv import load_dotenv

# Make src accessible
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from search import search_papers
from download import select_and_download_pdfs
from dataset import prepare_dataset


def sanitize_topic(topic):
    return topic.lower().replace(" ", "_")


def main():
    load_dotenv()

    api_key = os.getenv("CORE_API_KEY")
    if not api_key:
        raise Exception("CORE_API_KEY not found in .env")

    topic = input("Enter research topic: ").strip()
    if not topic:
        print("Topic cannot be empty")
        return

    safe_topic = sanitize_topic(topic)
    paper_folder = os.path.join("papers", safe_topic)

    print("\n🔍 Searching research papers...")
    papers = search_papers(topic, api_key, limit=20)

    print("⬇️ Downloading PDFs...")
    selected_papers = select_and_download_pdfs(
        papers,
        required_count=3,
        folder=paper_folder
    )

    if len(selected_papers) == 0:
        print("No valid PDFs found. Exiting.")
        return

    print(f"Total PDFs downloaded: {len(selected_papers)}")

    print("📊 Preparing dataset...")
    df = prepare_dataset(
        selected_papers,
        folder=paper_folder,
        topic=topic
    )

    csv_path = "research_dataset.csv"
    if os.path.exists(csv_path):
        df.to_csv(csv_path, mode="a", header=False, index=False)
    else:
        df.to_csv(csv_path, index=False)

    print("\n✅ Automation completed successfully")
    print(f"Topic: {topic}")
    print(f"Papers downloaded: {len(selected_papers)}")


if __name__ == "__main__":
    main()
