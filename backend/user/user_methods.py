# user_methods.py


def get_current_user(token: str) -> str:

    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=settings.ALGORITHM
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

    return decoded_token["user"]


def create_user(user: UserRegistration):
    """
    Creates a new user in the database.

    Parameters:
        user (UserRegistration): Input should be given as a JSON to the post method.

    Returns:
        JSONResponse: Returns a positive response when the user is created. Raises an exception otherwise.

    """
    user_exist = settings.USERS_DB.get(user.username)

    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username already registered.",
        )

    hashed_password = Hasher.hash_passw(user.password)
    user_in_db = UserInDB(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
    )
    settings.USERS_DB.update({user.username: user_in_db.dict()})
    save_users_db()
