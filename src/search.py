import requests

CORE_BASE_URL = "https://api.core.ac.uk/v3/search/works"

def search_papers(topic, api_key, limit=50):
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    params = {
        "q": topic,
        "limit": limit
    }

    try:
        response = requests.get(
            CORE_BASE_URL,
            headers=headers,
            params=params,
            timeout=30
        )

        if response.status_code != 200:
            print(f"CORE API error: {response.status_code}")
            return []

        data = response.json()
        return data.get("results", [])

    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return []
