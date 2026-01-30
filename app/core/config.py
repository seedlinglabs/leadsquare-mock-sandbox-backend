from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/leadsquared_db"
    SYNC_DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/leadsquared_db"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
