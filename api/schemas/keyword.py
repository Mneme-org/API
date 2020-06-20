from pydantic import BaseModel  # pylint: disable=no-name-in-module


class KeywordBase(BaseModel):
    word: str


class KeywordCreate(KeywordBase):
    pass


class Keyword(KeywordBase):
    id: int
    entry_id: int

    class Config:
        orm_mode = True
