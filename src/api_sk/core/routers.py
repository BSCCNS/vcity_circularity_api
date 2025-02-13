# routers.py

from fastapi import APIRouter, Security
from api_sk.auth import auth
from api_sk.core import endpoints
from api_sk.user import superuser_endpoints
from api_sk.auth.auth import check_superuser

# We define a router that collects everything together
api_router = APIRouter()
api_router.include_router(auth.router, prefix="")  # Security
api_router.include_router(endpoints.router, prefix="")  # Generic endpoint
api_router.include_router(
    superuser_endpoints.router,
    prefix="/superuser",
    dependencies=[Security(check_superuser, scopes=["superuser"])],
)  # User management endpoints
