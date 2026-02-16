import requests
import json
import os


def search_papers(query):
    url = "http://export.arxiv.org/api/query"

    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": 3
    }

    headers = {
        "User-Agent": "Synapse Research Bot 1.0"
    }

    papers = []

    try:
        response = requests.get(url, params=params, headers=headers, timeout=20)

        if response.status_code == 200:
            text = response.text
            entries = text.split("<entry>")[1:]

            for entry in entries:

                # Title
                try:
                    title = entry.split("<title>")[1].split("</title>")[0].strip()
                except:
                    title = "No title"

                # Paper Link
                try:
                    paper_link = entry.split("<id>")[1].split("</id>")[0].strip()
                except:
                    paper_link = "Not available"

                # PDF Link
                pdf_link = "Not available"
                if 'title="pdf"' in entry:
                    try:
                        pdf_link = entry.split('title="pdf" href="')[1].split('"')[0]
                    except:
                        pdf_link = "Not available"

                papers.append({
                    "title": title,
                    "paper_link": paper_link,
                    "pdf_link": pdf_link
                })

        else:
            print("API Error:", response.status_code)

    except requests.exceptions.RequestException as e:
        print("Connection Error:", e)

    return papers


if __name__ == "__main__":

    topic = input("Enter topic: ")
    papers = search_papers(topic)

    print("\nTop Papers:\n")

    for p in papers:
        print(p["title"])
        print(p["paper_link"])
        print(p["pdf_link"])
        print()

    # Save to JSON in project root folder
    BASE_DIR = os.getcwd()
    json_path = os.path.join(BASE_DIR, "papers.json")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=4)

print("Saving to:", json_path)
