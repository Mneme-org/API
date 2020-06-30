from typing import List, Optional
import datetime as dt
from tortoise.contrib.pydantic import PydanticModel

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
    date: dt.datetime
    deleted_on: Optional[dt.date] = None

    class Config:
        orm_mode = True
