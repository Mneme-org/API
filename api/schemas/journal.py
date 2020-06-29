from typing import List
from tortoise.contrib.pydantic import PydanticModel

from . import Entry


class JournalBase(PydanticModel):
    name: str


class JournalCreate(JournalBase):
    pass


class Journal(JournalBase):
    id: int
    entries: List[Entry] = []

    class Config:
        orm_mode = True
