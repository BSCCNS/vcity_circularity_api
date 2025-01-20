#routers.py

from fastapi import APIRouter
from auth import auth
from core import endpoints
from user import user_endpoints

# We define a router that collects everything together
api_router = APIRouter()
api_router.include_router(auth.router, prefix = "") # Security
api_router.include_router(endpoints.router, prefix = "") # Generic endpoint
api_router.include_router(user_endpoints.router, prefix = "/user") # User management endpoints