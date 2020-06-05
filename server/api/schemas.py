from typing import List

from pydantic import BaseModel


class Keyword(BaseModel):
    id: int
    entry_id: int
    word: str

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


class Journal(BaseModel):
    id: int
    pub_user_id: int
    name: str

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