import requests

CORE_BASE_URL = "https://api.core.ac.uk/v3/search/works"

def search_papers(topic, api_key, limit=5):
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    params = {
        "q": topic,
        "limit": limit
    }

    response = requests.get(
        CORE_BASE_URL,
        headers=headers,
        params=params
    )
    response.raise_for_status()

    return response.json().get("results", [])
