from pydantic import BaseModel


# Schemas for the token models

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None