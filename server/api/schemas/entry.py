from typing import List
from pydantic import BaseModel

from . import Keyword, KeywordCreate


class EntryBase(BaseModel):
    short: str
    long: str = ""
    date: str
    jrnl_id: int


class EntryCreate(EntryBase):
    keywords: List[KeywordCreate] = []


class Entry(EntryBase):
    id: int
    keywords: List[Keyword] = []

    class Config:
        orm_mode = True
