#auth.py
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from auth.hashing import *
from schemas.user_schema import *
from schemas.token_schema import *
from core.config import settings
import jwt
from jwt.exceptions import InvalidTokenError
from core.config import Settings

router = APIRouter()

# Loads the users DB
users_db = settings.USERS_DB

#Creates a Bearer scheme for authentication with OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_token(data: dict, expiration: timedelta|None = None):
    to_encode = data.copy()

    if expiration:
        exp = datetime.now(timezone.utc) + expiration
    else:
        exp = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({'exp': exp})
    encoded_token = jwt.encode(to_encode, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM)
    return encoded_token

#POST request for authentification and handling the token (in JWT format))

@router.post("/token")
async def token_request(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    
    # We query the username in the DB
    user_dict = users_db.get(form_data.username) 
    if not user_dict:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    
    # We now create an object user which stores the user data and we hash the password introduced by the user
    user = UserInDB(**user_dict)
    
    # Checks the password against the one stored in the DB
    if not Hasher.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    
    # And we now generate the token
    access_token_expires = timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"user": user.username}, expiration=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")