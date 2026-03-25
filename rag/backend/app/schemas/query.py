from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class QueryCreate(BaseModel):
    query_text: str
    user_id: int

class QueryRead(BaseModel):
    id: int
    query: str
    response: str
    user_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
