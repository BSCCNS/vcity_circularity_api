# superuser_endpoints.py

from fastapi import APIRouter, HTTPException, status
from cicloapi.core.config import settings
from fastapi.responses import JSONResponse



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
