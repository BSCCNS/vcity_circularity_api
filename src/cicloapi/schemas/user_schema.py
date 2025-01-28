# user_schema.py

from pydantic import BaseModel

# Schemas for user models


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    is_superuser: bool = False


class UserInDB(User):
    hashed_password: bytes | None = None


class UserRegistration(User):
    password: str
