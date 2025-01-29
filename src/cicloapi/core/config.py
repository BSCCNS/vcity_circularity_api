# config.py

from cicloapi.data.fake_db import users_db
import os
from dotenv import load_dotenv
from pathlib import Path

# Load the environment file
env_path = Path.home() / ".venv"
if env_path.exists():
    load_dotenv(env_path)

# Setting for the API

class Settings:
    PROJECT_NAME: str = "CicloAPI"
    DESCRIPTION: str = (
        "API for the ciclovias project."
    )
    CONTACT: dict[str] = {"name": "M. Herrero", "e-mail": "mherrero@bsc.es"}
    PROJECT_VERSION: str = "0.2"
    USERS_DB = users_db

    # Scopes for user authorization

    SCOPES = {
        "superuser": "User with rights to delete and administes database entries."
    }

    # Setting for token encoding (the secret key is Hex 32)
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15


settings = Settings()
