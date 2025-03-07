# config.py

from api_sk.data.fake_db import users_db
from dotenv import load_dotenv
import os
# Setting for the API
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Skeletor: a barebones API using FastAPI"
    DESCRIPTION: str = (
        "This is a basic API with standard funcionalities that will serve as a starting point to build a full API for a project."
    )
    CONTACT: dict[str] = {"name": "M. Herrero", "e-mail": "mherrero@bsc.es"}
    PROJECT_VERSION: str = "1.0"
    USERS_DB = users_db

    # Scopes for user authorization
    SCOPES = {
        "superuser": "User with rights to delete and administes database entries."
    }

    # Setting for token encoding (the secret key is Hex 32)
    SECRET_KEY = os.environ["SECRET_KEY"]
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15

settings = Settings()
