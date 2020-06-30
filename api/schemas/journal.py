from typing import List, Optional
from datetime import date

from tortoise.contrib.pydantic import PydanticModel

from . import Entry


class JournalBase(PydanticModel):
    name: str


class JournalCreate(JournalBase):
    pass


class Journal(JournalBase):
    id: int
    entries: List[Entry] = []
    deleted_on: Optional[date] = None

    class Config:
        orm_mode = True
