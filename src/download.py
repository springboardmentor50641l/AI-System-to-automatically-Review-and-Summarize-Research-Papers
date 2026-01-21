import os
import requests
import time

def select_and_download_pdfs(papers, required_count=3, folder="papers"):
    os.makedirs(folder, exist_ok=True)

    downloaded_papers = []

    for paper in papers:
        if len(downloaded_papers) >= required_count:
            break

        url = paper.get("downloadUrl")
        if not url:
            continue

        # Retry logic
        for attempt in range(3):
            try:
                response = requests.get(
                    url,
                    allow_redirects=True,
                    timeout=40
                )

                content_type = response.headers.get("Content-Type", "").lower()

                if "pdf" not in content_type:
                    break  # not a PDF, don't retry

                file_path = os.path.join(
                    folder, f"paper_{len(downloaded_papers) + 1}.pdf"
                )

                with open(file_path, "wb") as f:
                    f.write(response.content)

                downloaded_papers.append(paper)
                print(f"Downloaded PDF {len(downloaded_papers)}")
                break  # success, stop retrying

            except requests.exceptions.Timeout:
                print("Timeout occurred, retrying...")
                time.sleep(2)

            except Exception as e:
                print(f"Skipping paper due to error: {e}")
                break

    return downloaded_papers
