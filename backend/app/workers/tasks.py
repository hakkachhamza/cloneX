import asyncio
import json
from pathlib import Path
from uuid import UUID

from celery import states
from sqlalchemy import select

from app.workers.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.crawl_job import CrawlJob
from app.models.project import Project
from app.services.crawler_service import CrawlerService
from app.services.export_service import ExportService
from app.services.rewrite_service import RewriteService
from app.services.storage_service import StorageService


@celery_app.task(bind=True, max_retries=3)
def run_crawl_task(self, job_id: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run_crawl(self, job_id))
    finally:
        loop.close()


async def _run_crawl(self, job_id: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(CrawlJob).where(CrawlJob.id == UUID(job_id)))
        job = result.scalars().first()
        if not job:
            raise ValueError(f"Crawl job {job_id} not found")

        proj_result = await session.execute(select(Project).where(Project.id == job.project_id))
        project = proj_result.scalars().first()
        if not project:
            raise ValueError(f"Project {job.project_id} not found")

        if job.status in ("cancelled", "completed"):
            return {"status": job.status}

        job.status = "running"
        job.progress = 0
        await session.commit()

        start_url = project.source_url
        options = job.options or {}
        max_depth = options.get("max_depth", 2)
        max_pages = options.get("max_pages", 20)
        respect_robots = options.get("respect_robots", True)
        max_concurrent = options.get("max_concurrent", 8)
        wait_until = options.get("wait_until", "domcontentloaded")

        try:
            crawler = CrawlerService(
                start_url=start_url,
                max_depth=max_depth,
                max_pages=max_pages,
                respect_robots=respect_robots,
                max_concurrent=max_concurrent,
                wait_until=wait_until,
                page_timeout=20000,
            )

            self.update_state(state=states.STARTED, meta={"status": "crawling pages"})
            pages = await crawler.crawl()

            job.total_pages = len(pages)
            job.crawled_pages = sum(1 for r in pages.values() if r.status == 200)
            failed_pages = sum(1 for r in pages.values() if r.error)
            job.progress = max(1, int((job.crawled_pages / max(1, job.total_pages)) * 45))
            await session.commit()

            self.update_state(state=states.STARTED, meta={"status": "downloading assets"})
            asset_map = await crawler.download_assets()
            job.downloaded_assets = len(asset_map)
            job.progress = 70
            await session.commit()

            # Save raw assets to storage
            storage = StorageService()
            rewriter = RewriteService(
                base_url=start_url,
                asset_map=asset_map,
                replacements=project.replacements or {},
            )
            loop = asyncio.get_event_loop()
            total_assets = len(asset_map)
            for idx, (original_url, relative_path) in enumerate(asset_map.items()):
                try:
                    import requests

                    def fetch(u):
                        return requests.get(u, timeout=20, headers={"User-Agent": "cloneX/1.0"})

                    resp = await loop.run_in_executor(None, fetch, original_url)
                    if resp.status_code == 200:
                        content = resp.content
                        # Rewrite CSS paths
                        if relative_path.lower().endswith(".css"):
                            try:
                                text = resp.text
                                rewritten_css = rewriter.rewrite_css(text, original_url)
                                content = rewritten_css.encode("utf-8")
                            except Exception:
                                pass
                        # Basic JS sanitization: remove base origin references
                        if relative_path.lower().endswith(".js"):
                            try:
                                text = resp.text
                                text = text.replace(rewriter.base_origin, "")
                                content = text.encode("utf-8")
                            except Exception:
                                pass
                        storage.write_bytes(str(project.id), relative_path, content)
                except Exception as exc:
                    job.errors = (job.errors or []) + [f"Asset failed {original_url}: {exc}"]

                # Update progress during asset save
                if total_assets > 0:
                    job.progress = 70 + int((idx + 1) / total_assets * 15)
                    await session.commit()

            self.update_state(state=states.STARTED, meta={"status": "exporting project"})
            job.progress = 88
            await session.commit()

            export_service = ExportService(
                project_id=str(project.id),
                start_url=start_url,
                asset_map=asset_map,
                results=pages,
                replacements=project.replacements or {},
            )
            export_path = export_service.export_html()

            # Update project stats
            project.status = "ready"
            project.storage_path = export_path
            project.stats = {
                "pages": job.total_pages,
                "crawled_pages": job.crawled_pages,
                "assets": job.downloaded_assets,
                "errors": len(job.errors or []),
            }
            job.status = "completed"
            job.progress = 100
            await session.commit()

            return {
                "status": "completed",
                "project_id": str(project.id),
                "pages": job.total_pages,
                "assets": job.downloaded_assets,
                "path": export_path,
            }

        except Exception as exc:
            job.status = "failed"
            job.errors = (job.errors or []) + [str(exc)]
            project.status = "failed"
            await session.commit()
            self.update_state(state=states.FAILURE, meta={"exc": str(exc)})
            raise self.retry(exc=exc, countdown=10)
