#config.py

from data.fake_db import fake_users_db

class Settings:
    PROJECT_NAME: str = 'Skeletor'
    PROJECT_VERSION: str = '0.0.1'
    USERS_DB = fake_users_db

settings = Settings()