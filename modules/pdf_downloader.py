import requests
import os
import json

def download_pdfs():

    with open("papers.json", "r", encoding="utf-8") as f:
        papers = json.load(f)

    save_folder = "data/papers"
    os.makedirs(save_folder, exist_ok=True)

    for i, paper in enumerate(papers):

        pdf_link = paper.get("pdf_link")

        if pdf_link and pdf_link != "Not available":

            try:
                print("Downloading:", paper["title"])

                response = requests.get(pdf_link, timeout=20)

                file_path = os.path.join(save_folder, f"paper_{i+1}.pdf")

                with open(file_path, "wb") as f:
                    f.write(response.content)

                print("Saved:", file_path)

            except:
                print("Failed to download:", paper["title"])

        else:
            print("No PDF for:", paper["title"])


if __name__ == "__main__":
    download_pdfs()