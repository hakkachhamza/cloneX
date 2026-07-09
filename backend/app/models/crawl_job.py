import uuid

from sqlalchemy import Column, String, Text, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin


class CrawlJob(Base, TimestampMixin):
    __tablename__ = "crawl_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    celery_task_id = Column(String, nullable=True)
    status = Column(String, default="queued", nullable=False)
    progress = Column(Integer, default=0, nullable=False)
    total_pages = Column(Integer, default=0, nullable=False)
    crawled_pages = Column(Integer, default=0, nullable=False)
    downloaded_assets = Column(Integer, default=0, nullable=False)
    errors = Column(JSON, default=list, nullable=False)
    logs = Column(JSON, default=list, nullable=False)
    options = Column(JSON, default=dict, nullable=False)

    project = relationship("Project", back_populates="crawl_jobs")
