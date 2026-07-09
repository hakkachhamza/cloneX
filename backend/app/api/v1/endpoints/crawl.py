from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.crawl_job import CrawlJob
from app.models.project import Project
from app.models.user import User
from app.schemas.crawl_job import CrawlJobCreate, CrawlJobRead, CrawlJobUpdate
from app.core.auth import get_current_user
from app.workers.tasks import run_crawl_task

router = APIRouter()


@router.get("/", response_model=List[CrawlJobRead])
async def list_crawl_jobs(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(CrawlJob)
        .join(Project)
        .where(Project.owner_id == current_user.id)
        .order_by(CrawlJob.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=CrawlJobRead, status_code=201)
async def start_crawl(
    job_in: CrawlJobCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Project).where(
            Project.id == job_in.project_id,
            Project.owner_id == current_user.id,
        )
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    job = CrawlJob(
        project_id=job_in.project_id,
        status="queued",
        options=job_in.options or {},
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    task = run_crawl_task.delay(str(job.id))
    job.celery_task_id = task.id
    await session.commit()
    await session.refresh(job)
    return job


@router.get("/{job_id}", response_model=CrawlJobRead)
async def get_crawl_job(
    job_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(CrawlJob)
        .join(Project)
        .where(CrawlJob.id == job_id, Project.owner_id == current_user.id)
    )
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    return job


@router.patch("/{job_id}/pause", response_model=CrawlJobRead)
async def pause_crawl_job(
    job_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(CrawlJob)
        .join(Project)
        .where(CrawlJob.id == job_id, Project.owner_id == current_user.id)
    )
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    if job.status != "running":
        raise HTTPException(status_code=400, detail="Job is not running")
    job.status = "paused"
    await session.commit()
    await session.refresh(job)
    return job


@router.patch("/{job_id}/resume", response_model=CrawlJobRead)
async def resume_crawl_job(
    job_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(CrawlJob)
        .join(Project)
        .where(CrawlJob.id == job_id, Project.owner_id == current_user.id)
    )
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    if job.status != "paused":
        raise HTTPException(status_code=400, detail="Job is not paused")
    job.status = "queued"
    await session.commit()
    await session.refresh(job)

    task = run_crawl_task.delay(str(job.id))
    job.celery_task_id = task.id
    await session.commit()
    await session.refresh(job)
    return job


@router.patch("/{job_id}/cancel", response_model=CrawlJobRead)
async def cancel_crawl_job(
    job_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(CrawlJob)
        .join(Project)
        .where(CrawlJob.id == job_id, Project.owner_id == current_user.id)
    )
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    if job.celery_task_id:
        from app.workers.celery_app import celery_app
        celery_app.control.revoke(job.celery_task_id, terminate=True)
    job.status = "cancelled"
    await session.commit()
    await session.refresh(job)
    return job
