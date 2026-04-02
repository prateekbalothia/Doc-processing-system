from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    filename: str
    status: str
    created_at: datetime

    class Config:
        orm_mode = True