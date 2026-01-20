import os
import time
import requests

from dotenv import load_dotenv
load_dotenv()

#--------------API SETUP--------------
API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

HEADERS = {
    "x-api-key": API_KEY
}

#--------------SEARCH FUNCTION--------------
def search_papers(topic, limit=3):
    """
    Search research papers from Semantic Scholar based on topic.
    Returns a LIST of selected papers.
    """
    params = {
        "query": topic,
        "limit": limit,
        "fields": "paperId,title,authors,year,abstract,url,openAccessPdf"
    }

    response = requests.get(BASE_URL, headers=HEADERS, params=params)

    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

    #Return paper list
    return response.json().get("data", [])

#--------------MAIN SCRIPT--------------
if __name__ == "__main__":
    topic = input("Enter research topic: ").strip()

    if not topic:
        print("Topic cannot be empty.")
        exit(1)

    print(f"\nSearching papers for topic: {topic}\n")

    #--------------PAPER LIST--------------
    papers = search_papers(topic)
    print(f"Selected {len(papers)} papers:\n")

    for idx, paper in enumerate(papers, start=1):
        print(f"Paper {idx}:")
        print("Title:", paper.get("title"))
        print("Year:", paper.get("year"))
        print("URL:", paper.get("url"))
        print("-" * 40)

        time.sleep(1)

    # --------------CONNECTION--------------
    from download_papers import download_selected_papers
    download_selected_papers(papers)
    from download_papers import save_metadata
    save_metadata(papers)
