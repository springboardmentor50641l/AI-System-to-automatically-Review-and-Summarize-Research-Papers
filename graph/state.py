from pydantic import BaseModel
from typing import List, Optional


class WorkflowState(BaseModel):
    # Inputs
    topic: str
    mode: str
    texts: List[str]

    # Intermediate
    analysis: Optional[str] = None
    draft: Optional[str] = None
    reviewed: Optional[str] = None
