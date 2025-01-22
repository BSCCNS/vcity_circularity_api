#config.py

from data.fake_db import *

#Setting for the API

class Settings:
    PROJECT_NAME: str = 'Skeletor: a barebones API using FastAPI'
    DESCRIPTION: str = 'This is a basic API with standard funcionalities that will serve as a starting point to build a full API for a project.'
    CONTACT: dict[str] = {'name': 'M. Herrero', 'e-mail': 'mherrero@bsc.es'}
    PROJECT_VERSION: str = '0.0.3'
    USERS_DB = users_db

    #Scopes for user authorization
   
    SCOPES= {'superuser': 'User with rights to delete and administes database entries.'}

    #Setting for token encoding (the secret key is Hex 32)
    SECRET_KEY = '536813181b97e9b63698643c2c8b4edc44b78ca41071a1c92bc9ebdbc09c32de'
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 15

settings = Settings()