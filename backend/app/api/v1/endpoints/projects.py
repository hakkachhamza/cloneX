import os
import shutil
from pathlib import Path
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.core.auth import get_current_user
from app.services.project_service import delete_project_storage
from app.services.export_service import ExportService

router = APIRouter()


@router.get("/", response_model=List[ProjectRead])
async def list_projects(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    result = await session.execute(
        select(Project)
        .where(Project.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(Project.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=ProjectRead, status_code=201)
async def create_project(
    project_in: ProjectCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = Project(
        owner_id=current_user.id,
        name=project_in.name,
        source_url=str(project_in.source_url),
        export_format=project_in.export_format,
        status="pending",
        stats={},
        replacements=project_in.replacements or {},
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: UUID,
    project_in: ProjectUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project_in.name is not None:
        project.name = project_in.name
    if project_in.status is not None:
        project.status = project_in.status
    if project_in.replacements is not None:
        project.replacements = project_in.replacements
    await session.commit()
    await session.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.storage_path:
        delete_project_storage(project.storage_path)

    await session.delete(project)
    await session.commit()
    return None


@router.get("/{project_id}/preview")
async def preview_project(
    project_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.storage_path:
        raise HTTPException(status_code=400, detail="Project has not been exported yet")

    index_path = Path(project.storage_path) / "pages" / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Preview not available")

    html = index_path.read_text(encoding="utf-8")
    base_href = f"/api/projects/{project_id}/pages/"
    if "<base" not in html:
        html = html.replace("<head>", f'<head><base href="{base_href}">', 1)
    return HTMLResponse(content=html)


@router.get("/{project_id}/pages/{page_path:path}")
async def serve_project_page(
    project_id: UUID,
    page_path: str,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.storage_path:
        raise HTTPException(status_code=400, detail="Project has not been exported yet")

    page_file = Path(project.storage_path) / "pages" / page_path
    try:
        page_file.resolve().relative_to((Path(project.storage_path) / "pages").resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    if not page_file.exists() or not page_file.is_file():
        raise HTTPException(status_code=404, detail="Page not found")

    html = page_file.read_text(encoding="utf-8")
    base_href = f"/api/projects/{project_id}/pages/"
    if "<base" not in html:
        html = html.replace("<head>", f'<head><base href="{base_href}">', 1)
    return HTMLResponse(content=html)


@router.get("/{project_id}/assets/{file_path:path}")
async def serve_project_asset(
    project_id: UUID,
    file_path: str,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.storage_path:
        raise HTTPException(status_code=400, detail="Project has not been exported yet")

    asset_path = Path(project.storage_path) / file_path
    # Security: prevent directory traversal
    try:
        asset_path.resolve().relative_to(Path(project.storage_path).resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    if not asset_path.exists() or not asset_path.is_file():
        raise HTTPException(status_code=404, detail="Asset not found")
    return FileResponse(asset_path)


@router.get("/{project_id}/download")
async def download_project(
    project_id: UUID,
    format: str = Query("zip", enum=["zip", "html"]),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.storage_path:
        raise HTTPException(status_code=400, detail="Project has not been exported yet")

    base_path = Path(project.storage_path)
    if format == "html":
        index_path = base_path / "pages" / "index.html"
        return FileResponse(index_path, filename=f"{project.name}.html")

    # ZIP export
    zip_dir = base_path.parent / "exports"
    zip_dir.mkdir(parents=True, exist_ok=True)
    zip_path = zip_dir / f"{project.id}.zip"

    if zip_path.exists():
        zip_path.unlink()

    shutil.make_archive(str(zip_path.with_suffix("")), "zip", base_path)

    return FileResponse(zip_path, filename=f"{project.name}.zip", media_type="application/zip")
