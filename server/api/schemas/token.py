from pydantic import BaseModel  # pylint: disable=no-name-in-module


class Token(BaseModel):
    access_token: str
    # Give access to the person who has that token, no questions asked
    token_type: str = "bearer"


class TokenData(BaseModel):
    public_id: str
