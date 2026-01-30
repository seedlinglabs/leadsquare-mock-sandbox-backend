from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.database import init_db
from app.api.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="LeadSquared Mock API",
    description="A mock CRM backend API for managing users and leads",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "LeadSquared Mock API", "docs": "/docs"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
