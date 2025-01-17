#auth.py

from typing import Annotated
from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from auth.hashing import Hasher
from schemas.user_schema import *
from core.config import settings

router = APIRouter()

# Loads the users DB
users_db = settings.USERS_DB

#Creates a Bearer scheme for authentication with OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#POST request for authentification and handling the token (plain token for now)

@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # We query the username in the DB
    user_dict = users_db.get(form_data.username) 
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # We now create an object user which stores the user data and we hash the password introduced by the user
    user = UserInDB(**user_dict)
    hashed_password = Hasher.hash_passw(form_data.password)
    
    # Checks the password against the one stored in the DB
    if not user.hashed_password == hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # The token returned is trivial for now, we need to implement JWT
    return {"access_token": user.username, "token_type": "bearer"}