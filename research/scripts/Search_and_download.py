import os
import re
import json
import time
import argparse
import requests
from pathlib import Path


SEMANTIC_SCHOLAR_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
DEFAULT_FIELDS = "title,year,authors,url,openAccessPdf,isOpenAccess"


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def safe_filename(name: str, max_len: int = 120) -> str:
    name = re.sub(r"[\\/:*?\"<>|]+", "", name)
    name = name.strip()
    if len(name) > max_len:
        name = name[:max_len].strip()
    return name


def semantic_scholar_search(query: str, limit: int = 10, api_key: str | None = None):
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key

    params = {
        "query": query,
        "limit": limit,
        "fields": DEFAULT_FIELDS,
    }

    # perform request with basic retry/backoff on rate limit (HTTP 429)
    retries = 3
    backoff = 1.0
    while True:
        resp = requests.get(
            SEMANTIC_SCHOLAR_SEARCH_URL,
            params=params,
            headers=headers,
            timeout=60
        )
        if resp.status_code == 429:
            # rate limited; respect Retry-After header if present
            retry_after = resp.headers.get("Retry-After")
            try:
                wait = float(retry_after) if retry_after is not None else backoff
            except ValueError:
                wait = backoff
            print(f"⚠️  Rate limited by Semantic Scholar API, sleeping {wait}s before retry")
            time.sleep(wait)
            retries -= 1
            if retries <= 0:
                # give up and raise the error so caller can handle it
                resp.raise_for_status()
            backoff *= 2
            continue
        # for other statuses raise exception normally
        resp.raise_for_status()
        break

    data = resp.json()
    return data.get("data", [])


def download_pdf(pdf_url: str, out_path: Path) -> bool:
    try:
        with requests.get(pdf_url, stream=True, timeout=90) as r:
            r.raise_for_status()

            content_type = r.headers.get("Content-Type", "").lower()
            if "pdf" not in content_type and not pdf_url.lower().endswith(".pdf"):
                return False

            out_path.parent.mkdir(parents=True, exist_ok=True)

            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 128):
                    if chunk:
                        f.write(chunk)

        # size sanity check
        if out_path.exists() and out_path.stat().st_size < 20_000:
            return False

        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Search Semantic Scholar and download PDFs into papers/<topic_slug>/"
    )
    parser.add_argument("topic", type=str, help="Topic to search (from terminal)")
    parser.add_argument("--limit", type=int, default=10, help="How many papers to fetch (default 10)")
    parser.add_argument("--sleep", type=float, default=1.0, help="Delay between downloads (default 1.0 sec)")
    args = parser.parse_args()

    topic = args.topic.strip()
    if not topic:
        raise ValueError("Topic cannot be empty")

    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

    topic_slug = slugify(topic)
    topic_folder = Path("papers") / topic_slug

    # If the topic folder already exists and contains any files, assume
    # previous run has already handled this topic. Skip search/download.
    if topic_folder.exists() and any(topic_folder.iterdir()):
        print(f"✅ Topic folder '{topic_folder}' already exists, skipping search and download.")
        return

    topic_folder.mkdir(parents=True, exist_ok=True)

    print(f"\n🔎 Searching Semantic Scholar for: {topic}")
    try:
        papers = semantic_scholar_search(topic, limit=args.limit, api_key=api_key)
    except requests.exceptions.HTTPError as exc:
        print(f"❌ HTTP error during search: {exc}")
        print("You may be rate limited or have an invalid API key. Try again later or set SEMANTIC_SCHOLAR_API_KEY.")
        return

    if not papers:
        print("❌ No papers found.")
        return

    meta_list = []
    downloaded = 0

    for i, p in enumerate(papers, start=1):
        title = p.get("title") or f"paper_{i}"
        year = p.get("year") or "unknown"
        authors = p.get("authors") or []
        authors_str = ", ".join([a.get("name", "") for a in authors[:5]])

        open_pdf = p.get("openAccessPdf")
        pdf_url = None
        if open_pdf and isinstance(open_pdf, dict):
            pdf_url = open_pdf.get("url")

        if not pdf_url:
            print(f"⚠️ Skipping (no open PDF): {title[:80]}")
            continue

        safe_title = safe_filename(title)
        pdf_name = f"{i:02d}_{safe_title}_{year}.pdf"
        pdf_path = topic_folder / pdf_name

        print(f"\n⬇️ Downloading: {title[:80]}")
        ok = download_pdf(pdf_url, pdf_path)

        if ok:
            downloaded += 1
            print(f"✅ Saved: {pdf_path}")

            meta_list.append({
                "title": title,
                "year": year,
                "authors": authors_str,
                "pdf_url": pdf_url,
                "local_path": str(pdf_path)
            })
        else:
            print("❌ Download failed.")

        time.sleep(args.sleep)

    meta_path = topic_folder / "metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_list, f, indent=2, ensure_ascii=False)

    print("\n==============================")
    print(f"📂 Topic folder: {topic_folder}")
    print(f"📄 Downloaded PDFs: {downloaded}")
    print(f"🧾 Metadata saved: {meta_path}")
    print("==============================\n")


if __name__ == "__main__":
    main()
