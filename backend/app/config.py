from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "cloneX"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"

    frontend_url: str = "http://localhost:3000"

    database_url: str = "postgresql+asyncpg://cloneforge:cloneforge_secret@db:5432/cloneforge"

    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"

    storage_type: str = "local"
    storage_local_path: str = "./storage/projects"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: Optional[str] = None
    s3_bucket_name: Optional[str] = None
    s3_endpoint_url: Optional[str] = None

    access_token_expire_minutes: int = 60
    max_crawl_depth: int = 5
    max_concurrent_requests: int = 8
    allow_private_networks: bool = False

    first_superuser_email: str = "admin@cloneforge.local"
    first_superuser_password: str = "admin"

    @property
    def cors_origins(self) -> List[str]:
        return [self.frontend_url]


@lru_cache
def get_settings() -> Settings:
    return Settings()
