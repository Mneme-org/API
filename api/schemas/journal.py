from typing import List
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from . import Entry


class JournalBase(BaseModel):
    name: str


class JournalCreate(JournalBase):
    pass


class Journal(JournalBase):
    id: int
    entries: List[Entry] = []

    class Config:
        orm_mode = True
