import os

from dotenv import load_dotenv

from api_sk.__version__ import __version__
from api_sk.data.fake_db import users_db

# Setting for the API
load_dotenv()


class Settings:
    PROJECT_NAME: str = "vCity-circular-api"
    DESCRIPTION: str = "Circular index API for the vCity project."
    CONTACT: dict[str, str] = {"name": "M. Herrero", "e-mail": "mherrero@bsc.es"}
    PROJECT_VERSION: str = __version__
    USERS_DB = users_db

    # Scopes for user authorization
    SCOPES = {
        "superuser": "User with rights to delete and administes database entries."
    }

    # Setting for token encoding (the secret key is Hex 32)
    SECRET_KEY = os.environ["SECRET_KEY"]
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15

    # weighted sum tolerance
    TOLERANCE = os.getenv("TOLERANCE", 0.001)


settings = Settings()
