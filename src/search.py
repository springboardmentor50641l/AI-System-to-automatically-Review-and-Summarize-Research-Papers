import requests
import feedparser

CORE_BASE_URL = "https://api.core.ac.uk/v3/search/outputs"


#Core search

def search_core(topic, api_key, limit=10):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    params = {
        "q": topic,
        "limit": limit,
        "offset": 0
    }

    try:
        response = requests.get(
            CORE_BASE_URL,
            headers=headers,
            params=params,
            timeout=20
        )

        if response.status_code != 200:
            print(f"CORE API error: {response.status_code}")
            return []

        data = response.json()
        results = data.get("results", [])

        valid_results = []

        for paper in results:
            if paper.get("downloadUrl"):
                valid_results.append({
                    "title": paper.get("title"),
                    "downloadUrl": paper.get("downloadUrl")
                })

        print(f"CORE returned {len(valid_results)} valid papers")
        return valid_results

    except Exception as e:
        print("CORE failed:", e)
        return []


#Arxiv search(FALLBACK)

def search_arxiv(topic, limit=10):
    print("Using arXiv fallback...")

    url = "http://export.arxiv.org/api/query"

    params = {
        "search_query": f"all:{topic}",
        "start": 0,
        "max_results": limit
    }

    response = requests.get(url, params=params, timeout=20)
    feed = feedparser.parse(response.text)

    results = []

    for entry in feed.entries:
        pdf_link = None

        for link in entry.links:
            if "pdf" in link.href:
                pdf_link = link.href
                break

        # Fallback method
        if not pdf_link:
            pdf_link = entry.id.replace("abs", "pdf") + ".pdf"

        if pdf_link:
            results.append({
                "title": entry.title,
                "downloadUrl": pdf_link
            })

    print(f"arXiv returned {len(results)} papers")
    return results


#main search func

def search_papers(topic, api_key, limit=10):
    core_results = search_core(topic, api_key, limit)

    if core_results:
        return core_results

    return search_arxiv(topic, limit)