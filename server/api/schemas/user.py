from typing import List
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from . import Journal


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    public_id: str

    journals: List[Journal] = []

    class Config:
        orm_mode = True
