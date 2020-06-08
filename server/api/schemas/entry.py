from typing import List
from pydantic import BaseModel

from . import Keyword, KeywordCreate


class EntryBase(BaseModel):
    short: str
    long: str = ""
    date: str


class EntryCreate(EntryBase):
    keywords: List[KeywordCreate] = []


class Entry(EntryBase):
    id: int
    jrnl_id: int
    keywords: List[Keyword] = []

    class Config:
        orm_mode = True
