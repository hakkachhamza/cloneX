from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CrawlJobBase(BaseModel):
    pass


class CrawlJobCreate(BaseModel):
    project_id: UUID
    options: Optional[Dict[str, Any]] = {}


class CrawlJobUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[int] = None
    total_pages: Optional[int] = None
    crawled_pages: Optional[int] = None
    downloaded_assets: Optional[int] = None
    errors: Optional[List[str]] = None
    logs: Optional[List[str]] = None


class CrawlJobRead(CrawlJobBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    celery_task_id: Optional[str] = None
    status: str
    progress: int
    total_pages: int
    crawled_pages: int
    downloaded_assets: int
    errors: List[str]
    logs: List[str]
    options: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
