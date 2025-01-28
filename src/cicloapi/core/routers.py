# routers.py

from fastapi import APIRouter, Security
from cicloapi.auth import auth
from cicloapi.core import endpoints
from cicloapi.user import superuser_endpoints

# We define a router that collects everything together
api_router = APIRouter()
api_router.include_router(auth.router, prefix="")  # Security
api_router.include_router(endpoints.router, prefix='/tasks')  # API endpoints
api_router.include_router(
    superuser_endpoints.router,
    prefix="/superuser",
    dependencies=[Security(auth.check_superuser, scopes=["superuser"])],
)  # User management endpoints
