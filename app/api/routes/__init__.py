from fastapi import APIRouter

from app.api.routes.users import router as users_router
from app.api.routes.leads import router as leads_router

api_router = APIRouter()

api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(leads_router, prefix="/leads", tags=["leads"])
