from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, HttpUrl, ConfigDict


class ProjectBase(BaseModel):
    name: str
    source_url: HttpUrl
    export_format: str = "html"


class ProjectCreate(ProjectBase):
    replacements: Optional[Dict[str, Any]] = {}
    options: Optional[Dict[str, Any]] = {}


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    replacements: Optional[Dict[str, Any]] = None


class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    status: str
    storage_path: Optional[str] = None
    stats: Dict[str, Any]
    replacements: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
