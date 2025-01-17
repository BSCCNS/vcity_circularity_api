#config.py

from data.fake_db import fake_users_db

class Settings:
    PROJECT_NAME: str = 'Skeletor: a barebones API sugin FastAPI'
    DESCRIPTION: str = 'This is a basic API with standard funcionalities that will serve as a starting point to build a full API for a project.'
    CONTACT: dict[str] = {'name': 'M. Herrero', 'e-mail': 'mherrero@bsc.es'}
    PROJECT_VERSION: str = '0.0.1'
    USERS_DB = fake_users_db

settings = Settings()