from pydantic import BaseModel
from typing import List, Any

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    limit: int

    model_config = {"from_attributes": True }
