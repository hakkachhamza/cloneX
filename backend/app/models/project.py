import uuid

from sqlalchemy import Column, String, Text, ForeignKey, Integer, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    source_url = Column(String, nullable=False)
    status = Column(String, default="pending", nullable=False)
    storage_path = Column(String, nullable=True)
    stats = Column(JSON, default=dict, nullable=False)
    replacements = Column(JSON, default=dict, nullable=False)
    export_format = Column(String, default="html", nullable=False)

    owner = relationship("User", back_populates="projects")
    crawl_jobs = relationship("CrawlJob", back_populates="project", cascade="all, delete-orphan")
