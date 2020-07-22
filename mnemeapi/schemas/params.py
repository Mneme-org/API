from typing import Optional
from pydantic import BaseModel  # pylint: disable=no-name-in-module

class Params(BaseModel):
    """Parameters for finding entries"""
    jrnl_name: Optional[str] = None
    date_min: Optional[str] = None  # YYYY-MM-DD HH:MM (with hour and minutes being optional)
    date_max: Optional[str] = None  # YYYY-MM-DD HH:MM (with hour and minutes being optional)
    skip: int = 0
    limit: int = 100
    method: str
