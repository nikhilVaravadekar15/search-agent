from typing import List, Dict, Optional

from pydantic import BaseModel


class ApiResponseModel(BaseModel):
    status: int
    message: str
    data: Optional[Dict | List] = None
    success: bool
