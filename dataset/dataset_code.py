import csv
import os
from datetime import datetime
def add_paper(id,title,authors,year,topic,source,path,selection,selection_reason):
    dataset_folder="dataset"
    csv_path=os.path.join(dataset_folder,"dataset_of_papers.csv")
    os.makedirs(dataset_folder,exist_ok=True)
    file_exists=os.path.isfile(csv_path)
    with open(csv_path,mode="a",newline="",encoding="utf-8") as file:
        writer=csv.writer(file)
        if not file_exists:
            writer.writerow(["id","title","authors","year","topic","source","path","selection","selection_reason"])
        writer.writerow([id,title,authors,year,topic,source,path,selection,selection_reason])
        