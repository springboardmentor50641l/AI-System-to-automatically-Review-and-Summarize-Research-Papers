import os
import requests
import time

def select_and_download_pdfs(papers, required_count=3, folder="papers"):
    os.makedirs(folder, exist_ok=True)

    downloaded = []
    failed = []

    for paper in papers:
        if len(downloaded) >= required_count:
            break

        url = paper.get("downloadUrl")
        if not url:
            failed.append(paper)
            continue

        try:
            response = requests.get(url, allow_redirects=True, timeout=40)
            content_type = response.headers.get("Content-Type", "").lower()

            if "pdf" not in content_type:
                failed.append(paper)
                continue

            file_path = os.path.join(
                folder, f"paper_{len(downloaded) + 1}.pdf"
            )

            with open(file_path, "wb") as f:
                f.write(response.content)

            downloaded.append(paper)
            print(f"Downloaded PDF {len(downloaded)}")

        except Exception:
            failed.append(paper)

    return downloaded, failed
