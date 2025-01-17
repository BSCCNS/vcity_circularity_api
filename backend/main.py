#main.py

from fastapi import FastAPI, Depends
from core.config import settings
from core.routers import api_router
from typing import Annotated
from fastapi.security import *

app = FastAPI(title=settings.PROJECT_NAME,version=settings.PROJECT_VERSION)
app.include_router(api_router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/")
def hello_api(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"msg":"By the Power of Grayskull! I have the power!"}