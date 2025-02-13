from pydantic import BaseModel


# Schemas for the token models


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(Token):
    scopes: list[str] = []
