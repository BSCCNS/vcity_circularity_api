# endpoints.py
from typing import Annotated
from fastapi import Depends, APIRouter
from auth.auth import *

router = APIRouter()


# Generic example of a GET endpoint


@router.get("/")
async def hello_api(token: Annotated[str, Depends(check_token)]):
    """'
    GET call to /. Returns a hello message. User must be authenticated.

    """
    return {"msg": "By the Power of Grayskull! I have the power!"}
