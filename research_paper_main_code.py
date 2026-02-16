from dataset.dataset_code import add_paper
import requests
import os 
from datetime import datetime
from pathlib import Path
from pipelines.langgraph_text_extraction_graph import pipeline
from pipelines.key_finding import run_key_findings
from pipelines.compare_papers import run_review_builder
from comparision_id import generate_comparison_id
from pipelines.draft_generation import build_final_literature_review


comparison_id = generate_comparison_id()
index=1
pdf_paper=[]
pdf=0
#API KEY
APIKEY="ZTfQ0m7guB358k9hi3j0T3wPVox2KsNB6IVTOhaq"
#input topic and folder to store papers
topic=input("ENTER RESEARCH TOPIC:")
safe_topic = topic.replace(" ", "_")
time=datetime.now().strftime("%y%m%d_%H%M%S")
folder = f"papers/{safe_topic}_{time}"
os.makedirs(folder)
#extract metadata
url="https://api.semanticscholar.org/graph/v1/paper/search"
headers={"x-api-key":APIKEY}
params={"query":topic,"limit":30,"fields": "title,year,authors,openAccessPdf"}
response=requests.get(url,headers=headers,params=params)
data = response.json()

if "data" not in data:
    print("API response error:", data)
    exit()
for paper in data["data"]:
    if len(pdf_paper) == 6:
        break  
    info=paper.get("openAccessPdf")
    if info and info.get("url"):
        pdf_paper.append(paper)
        pdf+=1
        print(pdf,"pdf",paper["title"])
    else:
        print(("no pdf",paper["title"]))
#extracting metadata
successful_papers = []
downloaded_papers = []
metadata_list=[]

for paper in pdf_paper:
    pdf_url=paper["openAccessPdf"]["url"]
    download=requests.get(pdf_url)
    if download.status_code==200:
        filename=f"{folder}/{safe_topic}_paper_{index}.pdf"
        with open(filename,"wb") as f:
            f.write(download.content)
        print("DOWNLOADED:",filename) 
        
                  
        title = paper["title"]
        paper_id = f"P{index}_{safe_topic}_{time}"
        authors = ", ".join([a["name"] for a in paper.get("authors", [])])
        year = paper.get("year", "Unknown")
        source = "Semantic Scholar"
        selected = "yes"
        selection_reason = "Open-access PDF available"
        index+=1 
        downloaded_papers.append((paper_id, filename))
        metadata = {"title": title,"authors": authors,"year": year,"source": source}

        metadata_list.append(metadata)

        #dataset
        add_paper( paper_id,title,authors,year,topic,source,filename,selected,selection_reason)
#text extraction and semantic sectioning        
successful_papers = []

for paper_id, filename in downloaded_papers:
    if len(successful_papers) == 2:
        break
    try:
        result = pipeline.invoke({
            "pdf_path": filename,
            "paper_id": paper_id
        })

        print(f"Processed and sectioned: {paper_id}")
        successful_papers.append(paper_id)

    except Exception as e:
        print(f"FAILED processing {paper_id}: {e}")
        continue
#key finding and cross comparision        
if len(successful_papers) >= 2:
    for paper_id in successful_papers:
        run_key_findings(paper_id, comparison_id)
    run_review_builder(comparison_id)
    build_final_literature_review(comparison_id, metadata_list)

else:
    print("Not enough successfully processed papers for review.")
    


