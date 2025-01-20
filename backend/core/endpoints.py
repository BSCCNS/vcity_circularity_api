#endpoints.py
from typing import Annotated
from fastapi import Depends, APIRouter
from auth.auth import oauth2_scheme, check_token_expiration
from schemas.token_schema import Token

router = APIRouter()


@router.get("/")
def hello_api(token: Annotated[Token, Depends(check_token_expiration)]):
    ''''
    GET call to /. Returns a hello message. It needs a Beared head.

    '''
    return {"msg":"By the Power of Grayskull! I have the power!"}