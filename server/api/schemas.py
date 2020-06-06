from typing import List

from pydantic import BaseModel


class KeywordBase(BaseModel):
    word: str


class KeywordCreate(KeywordBase):
    pass


class Keyword(KeywordBase):
    id: int
    entry_id: int

    class Config:
        orm_mode = True


class Entry(BaseModel):
    id: int
    jrnl_id: int
    short: str
    long: str
    date: str
    keywords: List[Keyword] = []

    class Config:
        orm_mode = True


class JournalBase(BaseModel):
    name: str


class JournalCreate(JournalBase):
    pass


class Journal(JournalBase):
    id: int
    entries: List[Entry] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    public_id: str

    journals: List[Journal] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    # Give access to the person who has that token, no questions asked
    token_type: str = "bearer"

class TokenData(BaseModel):
    public_id: str