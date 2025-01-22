#routers.py

from fastapi import APIRouter, Security
from auth import auth
from core import endpoints
from user import superuser_endpoints
from auth.auth import *

# We define a router that collects everything together
api_router = APIRouter()
api_router.include_router(auth.router, prefix = "") # Security
api_router.include_router(endpoints.router, prefix = "") # Generic endpoint
api_router.include_router(superuser_endpoints.router, prefix = "/superuser",
                          dependencies=[Security(check_superuser, scopes=["superuser"])]
                          ) # User management endpoints