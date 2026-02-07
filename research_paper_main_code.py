from dataset.dataset_code import add_paper
import requests
import os 
from datetime import datetime
#from text_extraction.text_extraction_code import process_pdf
from pathlib import Path
index=1
pdf_paper=[]
pdf=0
#API KEY
APIKEY="ZTfQ0m7guB358k9hi3j0T3wPVox2KsNB6IVTOhaq"
#input topic and folder to store papers
topic=input("ENTER RESEARCH TOPIC:")
time=datetime.now().strftime("%y%m%d_%H%M%S")
folder=f"papers/{topic}_{time}"
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
    if len(pdf_paper) == 3:
        break  # STOP when we have 3 papers
    info=paper.get("openAccessPdf")
    if info and info.get("url"):
        pdf_paper.append(paper)
        pdf+=1
        print(pdf,"pdf",paper["title"])
    else:
        print(("no pdf",paper["title"]))
#extracting metadata
for paper in pdf_paper:
    pdf_url=paper["openAccessPdf"]["url"]
    download=requests.get(pdf_url)
    if download.status_code==200:
        filename=f"{folder}/{topic}_paper_{index}.pdf"
        with open(filename,"wb") as f:
            f.write(download.content)
        print("DOWNLOADED:",filename)                   
        title = paper["title"]
        paper_id = f"P{index}_{topic}"
        authors = ", ".join([a["name"] for a in paper.get("authors", [])])
        year = paper.get("year", "Unknown")
        source = "Semantic Scholar"
        selected = "yes"
        selection_reason = "Open-access PDF available"
        index+=1 
        #dataset
        add_paper( paper_id,title,authors,year,topic,source,filename,selected,selection_reason)
        #Text extraction
        #pdf_path = Path(filename)
        #output_base = Path(f"text_extraction/output/{paper_id}")
        #process_pdf(pdf_path, output_base)
        
