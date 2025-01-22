# user_endpoints.py

from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Security
from auth.hashing import *
from core.config import settings
from schemas.user_schema import *
from fastapi.responses import JSONResponse
from data.db_methods import *


router = APIRouter()

# Endpoints for user management


@router.delete("/delete_user")
async def delete_user(user: str, token: str):
    """
    Deletes a user from the database.

    Parameters:
        user (str): Username of the user to delete.

    Returns:
        JSONResponse: Returns a positive response when the user is deleted. Raises an exception otherwise.

    """

    user_exist = settings.USERS_DB.get(user)

    if not user_exist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Username not in database."
        )

    del settings.USERS_DB[user]

    return JSONResponse(
        content={"message": "User deleted from database.", "status": "ok"},
        status_code=200,
    )
