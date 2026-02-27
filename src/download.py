import os
import requests


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
            print(f"Trying to download: {url}")

            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=40,
                allow_redirects=True
            )

            if response.status_code != 200:
                print(f"Failed (status {response.status_code})")
                failed.append(paper)
                continue

            file_path = os.path.join(
                folder, f"paper_{len(downloaded) + 1}.pdf"
            )

            with open(file_path, "wb") as f:
                f.write(response.content)

            downloaded.append(file_path)
            print(f"Downloaded PDF {len(downloaded)}")

        except Exception as e:
            print(f"Download error: {e}")
            failed.append(paper)

    return downloaded, failed