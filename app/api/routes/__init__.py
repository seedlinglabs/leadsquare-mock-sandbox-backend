from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.leads import router as leads_router
from app.api.routes.appointments import router as appointments_router
from app.api.routes.dashboard import router as dashboard_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(leads_router, prefix="/leads", tags=["leads"])
api_router.include_router(appointments_router, prefix="/appointments", tags=["appointments"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
