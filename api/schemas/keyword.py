from tortoise.contrib.pydantic import PydanticModel


class KeywordBase(PydanticModel):
    word: str


class KeywordCreate(KeywordBase):
    pass


class Keyword(KeywordBase):
    id: int
    entry_id: int

    class Config:
        orm_mode = True
