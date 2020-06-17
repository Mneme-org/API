from typing import List
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from . import Keyword, KeywordCreate


class EntryBase(BaseModel):
    short: str
    long: str = ""
    date: str


class EntryCreate(EntryBase):
    keywords: List[KeywordCreate] = []


class EntryUpdate(EntryBase):
    keywords: List[KeywordCreate]
    jrnl_id: int


class Entry(EntryBase):
    id: int
    jrnl_id: int
    keywords: List[Keyword] = []

    class Config:
        orm_mode = True
