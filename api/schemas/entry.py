from typing import List
from datetime import datetime
from tortoise.contrib.pydantic import PydanticModel
# from pydantic import BaseModel  # pylint: disable=no-name-in-module

from . import Keyword, KeywordCreate


class EntryBase(PydanticModel):
    short: str
    long: str = ""
    # YYYY-MM-DD HH:MM format in UTC timezone
    date: str


class EntryCreate(EntryBase):
    keywords: List[KeywordCreate] = []


class EntryUpdate(EntryBase):
    keywords: List[KeywordCreate]
    journal_id: int


class Entry(EntryBase):
    id: int
    journal_id: int
    keywords: List[Keyword] = []
    date: datetime

    class Config:
        orm_mode = True
