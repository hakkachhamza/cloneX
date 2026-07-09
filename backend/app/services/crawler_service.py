import asyncio
import ipaddress
import re
import urllib.robotparser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from app.config import get_settings

settings = get_settings()


class URLValidationError(Exception):
    pass


@dataclass
class CrawlResult:
    url: str
    html: str
    status: int = 200
    assets: Dict[str, str] = field(default_factory=dict)
    links: List[str] = field(default_factory=list)
    error: Optional[str] = None


def is_private_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return True
    try:
        host = parsed.hostname
        if not host:
            return True
        if host.lower() in ("localhost", "127.0.0.1"):
            return True
        addr = ipaddress.ip_address(host)
        return addr.is_private or addr.is_loopback or addr.is_reserved
    except ValueError:
        # Hostname, resolve not performed; rely on block-list
        if host.lower().endswith(".local") or host.lower().endswith(".internal"):
            return True
    return False


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise URLValidationError("Only HTTP/HTTPS URLs are supported.")
    if not parsed.netloc:
        raise URLValidationError("Invalid URL.")
    if not settings.allow_private_networks and is_private_url(url):
        raise URLValidationError(
            "Private network / localhost targets are blocked by default. Enable ALLOW_PRIVATE_NETWORKS only for authorized infrastructure."
        )


def can_fetch(url: str, respect_robots: bool = True) -> bool:
    if not respect_robots:
        return True
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch("cloneX", url)
    except Exception:
        # If robots.txt is unreachable, assume allowed but log.
        return True


def normalize_url(url: str, base: str) -> str:
    full = urljoin(base, url)
    parsed = urlparse(full)
    # Remove fragment
    return urlunparse(parsed._replace(fragment=""))


def same_domain(url: str, base_domain: str) -> bool:
    parsed = urlparse(url)
    return parsed.netloc.lower() == base_domain.lower()


def sanitize_filename(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/") or "index"
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", path)
    if not name or name.endswith("/"):
        name += "index.html"
    if "." not in name.split("/")[-1]:
        name += ".html"
    return name


def guess_asset_folder(url: str) -> str:
    ext = Path(urlparse(url).path).suffix.lower()
    if ext in (".css",):
        return "css"
    if ext in (".js", ".mjs", ".ts"):
        return "js"
    if ext in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".bmp"):
        return "images"
    if ext in (".woff", ".woff2", ".ttf", ".otf", ".eot"):
        return "fonts"
    if ext in (".mp4", ".webm", ".ogv", ".mov"):
        return "videos"
    return "assets"


class CrawlerService:
    def __init__(
        self,
        start_url: str,
        max_depth: int = 3,
        max_pages: int = 30,
        respect_robots: bool = True,
        max_concurrent: int = 8,
        wait_until: str = "domcontentloaded",
        page_timeout: int = 20000,
    ):
        validate_url(start_url)
        self.start_url = start_url
        parsed = urlparse(start_url)
        self.base_domain = parsed.netloc.lower()
        self.base_origin = f"{parsed.scheme}://{parsed.netloc}"
        self.max_depth = max(1, min(max_depth, settings.max_crawl_depth))
        self.max_pages = max_pages
        self.respect_robots = respect_robots
        self.max_concurrent = max(1, max_concurrent)
        self.wait_until = wait_until
        self.page_timeout = page_timeout
        self.visited: Set[str] = set()
        self.results: Dict[str, CrawlResult] = {}
        self.asset_map: Dict[str, str] = {}
        self._page_semaphore = None

    async def crawl(self) -> Dict[str, CrawlResult]:
        if not can_fetch(self.start_url, self.respect_robots):
            raise URLValidationError("Crawling disallowed by robots.txt. Only proceed if you own this site.")

        self._page_semaphore = asyncio.Semaphore(self.max_concurrent)
        queue: asyncio.Queue = asyncio.Queue()
        await queue.put((self.start_url, 0))
        self.visited.add(self.start_url)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (compatible; cloneX/1.0; +https://clonex.local)"
            )

            workers = [
                asyncio.create_task(self._worker(queue, context))
                for _ in range(self.max_concurrent)
            ]
            await queue.join()
            for w in workers:
                w.cancel()
            await browser.close()

        return self.results

    async def _worker(self, queue: asyncio.Queue, context):
        while True:
            try:
                url, depth = await asyncio.wait_for(queue.get(), timeout=2.0)
            except asyncio.TimeoutError:
                return
            try:
                if depth > self.max_depth or len(self.results) >= self.max_pages:
                    queue.task_done()
                    continue
                result = await self._fetch_page(url, context)
                self.results[url] = result
                if depth < self.max_depth:
                    for link in result.links:
                        if link not in self.visited and same_domain(link, self.base_domain):
                            self.visited.add(link)
                            await queue.put((link, depth + 1))
            except Exception as exc:
                self.results[url] = CrawlResult(url=url, html="", status=0, error=str(exc))
            finally:
                queue.task_done()

    async def _fetch_page(self, url: str, context) -> CrawlResult:
        async with self._page_semaphore:
            page = await context.new_page()
            try:
                response = await page.goto(
                    url,
                    wait_until=self.wait_until,  # type: ignore
                    timeout=self.page_timeout,
                )
                html = await page.content()
                status = response.status if response else 0
            except Exception as exc:
                await page.close()
                return CrawlResult(url=url, html="", status=0, error=str(exc))

            soup = BeautifulSoup(html, "lxml")

            assets: Dict[str, str] = {}
            links: List[str] = []

            # Collect stylesheets
            for tag in soup.find_all("link", rel="stylesheet"):
                href = tag.get("href")
                if href:
                    full = normalize_url(href, url)
                    assets[full] = guess_asset_folder(full)

            # Collect scripts
            for tag in soup.find_all("script", src=True):
                src = tag.get("src")
                if src:
                    full = normalize_url(src, url)
                    assets[full] = guess_asset_folder(full)

            # Collect images
            for tag in soup.find_all("img"):
                src = tag.get("src") or tag.get("data-src")
                if src:
                    full = normalize_url(src, url)
                    assets[full] = "images"

            # Collect fonts in link preload / stylesheet will be handled by CSS parsing later
            for tag in soup.find_all("link"):
                href = tag.get("href")
                if href and (".woff" in href.lower() or ".ttf" in href.lower() or ".otf" in href.lower()):
                    full = normalize_url(href, url)
                    assets[full] = "fonts"

            # Collect internal links
            for tag in soup.find_all("a", href=True):
                href = tag.get("href")
                full = normalize_url(href, url)
                if same_domain(full, self.base_domain):
                    links.append(full)

            await page.close()
            return CrawlResult(url=url, html=html, status=status, assets=assets, links=list(set(links)))

    async def download_assets(self) -> Dict[str, str]:
        """Return a mapping from original asset URL to local relative path."""
        urls: Set[str] = set()
        for result in self.results.values():
            urls.update(result.assets.keys())

        async def fetch(url: str) -> tuple:
            try:
                loop = asyncio.get_event_loop()
                resp = await loop.run_in_executor(
                    None,
                    lambda: requests.get(url, timeout=20, headers={"User-Agent": "cloneX/1.0"}),
                )
                resp.raise_for_status()
                folder = guess_asset_folder(url)
                filename = sanitize_filename(url)
                if filename.endswith(".html"):
                    filename += Path(urlparse(url).path).suffix or ".bin"
                local_path = f"{folder}/{filename}"
                return url, local_path, resp.content
            except Exception as exc:
                return url, None, str(exc)

        semaphore = asyncio.Semaphore(self.max_concurrent * 2)

        async def bounded_fetch(url):
            async with semaphore:
                return await fetch(url)

        tasks = [bounded_fetch(u) for u in urls]
        downloaded = await asyncio.gather(*tasks)

        mapping: Dict[str, str] = {}
        for url, local_path, payload in downloaded:
            if local_path is None:
                continue
            mapping[url] = local_path
            self.asset_map[url] = local_path
        return mapping

    def get_sitemap_urls(self) -> List[str]:
        sitemap_url = urljoin(self.start_url, "/sitemap.xml")
        try:
            response = requests.get(sitemap_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
            return [loc.text for loc in soup.find_all("loc")]
        except Exception:
            return []
