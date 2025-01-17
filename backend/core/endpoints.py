#endpoints.py
from typing import Annotated
from fastapi import Depends, APIRouter
from auth.auth import oauth2_scheme

router = APIRouter()


@router.get("/")
def hello_api(token: Annotated[str, Depends(oauth2_scheme)]):
    ''''
    GET call to /. Returns a hello message. It needs a Beared head.

    '''
    return {"msg":"By the Power of Grayskull! I have the power!"}