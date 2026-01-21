from pydantic import BaseModel
from typing import List, Optional

class Paper(BaseModel):
    title: str
    year: Optional[int]
    pdf_path: str
    reason: str

class ResearchDataset(BaseModel):
    papers: List[Paper]
