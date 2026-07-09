import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Comment
import cssutils
import tinycss2

from app.services.crawler_service import guess_asset_folder, normalize_url, sanitize_filename


def get_local_path_for_url(asset_url: str, asset_map: dict) -> str:
    return asset_map.get(asset_url, asset_url)


class RewriteService:
    def __init__(
        self,
        base_url: str,
        asset_map: dict,
        replacements: dict,
    ):
        self.base_url = base_url
        self.base_parsed = urlparse(base_url)
        self.base_origin = f"{self.base_parsed.scheme}://{self.base_parsed.netloc}"
        self.asset_map = asset_map
        self.replacements = replacements
        self.placeholder_patterns = self._build_placeholder_patterns()

    def _build_placeholder_patterns(self) -> list:
        company_name = self.replacements.get("company_name") or "{{COMPANY_NAME}}"
        email = self.replacements.get("email") or "{{EMAIL}}"
        phone = self.replacements.get("phone") or "{{PHONE}}"
        address = self.replacements.get("address") or "{{ADDRESS}}"
        copyright_holder = self.replacements.get("copyright") or "{{COPYRIGHT}}"

        return [
            (re.compile(r"\b[A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)+\s*(Inc\.?|LLC|Ltd\.?|Corp\.?|Company)\b"), company_name),
            (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), email),
            (re.compile(r"\b(?:\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b"), phone),
            (re.compile(r"\b\d{1,5}\s+([A-Za-z0-9]+\s*){1,4}(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\.?\b", re.IGNORECASE), address),
            (re.compile(r"©\s*\d{4}\s*[A-Za-z0-9\s.,&-]+", re.IGNORECASE), f"© {copyright_holder}"),
        ]

    def rewrite_html(self, html: str, page_url: str) -> str:
        soup = BeautifulSoup(html, "lxml")

        # Remove analytics / tracking scripts and meta tags
        self._sanitize_tracking(soup)

        # Rewrite asset paths
        for tag in soup.find_all("link", rel="stylesheet"):
            href = tag.get("href")
            if href:
                local = self._to_local_asset(href, page_url)
                if local:
                    tag["href"] = local

        for tag in soup.find_all("script", src=True):
            src = tag.get("src")
            if src:
                local = self._to_local_asset(src, page_url)
                if local:
                    tag["src"] = local

        for tag in soup.find_all("img"):
            for attr in ("src", "data-src", "srcset"):
                val = tag.get(attr)
                if val:
                    if attr == "srcset":
                        tag[attr] = self._rewrite_srcset(val, page_url)
                    else:
                        local = self._to_local_asset(val, page_url)
                        if local:
                            tag[attr] = local

        for tag in soup.find_all("link"):
            href = tag.get("href")
            if href and ("icon" in tag.get("rel", []) or "shortcut" in tag.get("rel", [])):
                tag.decompose()
                continue
            if href:
                local = self._to_local_asset(href, page_url)
                if local:
                    tag["href"] = local

        # Rewrite internal links to local .html
        for tag in soup.find_all("a", href=True):
            href = tag.get("href")
            if href and self._is_internal(href):
                tag["href"] = self._to_local_page(href, page_url)
            elif href and href.startswith("http"):
                # External link: replace with placeholder or keep as-is depending on policy
                tag["href"] = "#"
                tag["target"] = "_blank"
                tag["rel"] = "noopener"

        # Replace branding in text
        self._replace_text_nodes(soup)

        # OG metadata / author
        for meta in soup.find_all("meta"):
            prop = meta.get("property", "").lower()
            name = meta.get("name", "").lower()
            if prop.startswith("og:") or name in ("author", "twitter:title", "twitter:description"):
                content = meta.get("content")
                if content:
                    meta["content"] = self._apply_replacements(content)

        # Title
        if soup.title:
            soup.title.string = self._apply_replacements(soup.title.get_text())

        return str(soup)

    def rewrite_css(self, css_text: str, css_url: str) -> str:
        try:
            sheet = cssutils.parseString(css_text)
            for rule in sheet:
                if rule.type == rule.FONT_FACE_RULE:
                    for prop in rule.style:
                        if prop.name.lower() == "src":
                            prop.value = self._rewrite_css_url_value(prop.value, css_url)
                if rule.type in (rule.STYLE_RULE, rule.MEDIA_RULE):
                    if hasattr(rule, "style"):
                        for prop in rule.style:
                            if "url(" in prop.value:
                                prop.value = self._rewrite_css_url_value(prop.value, css_url)
            return sheet.cssText.decode("utf-8") if isinstance(sheet.cssText, bytes) else sheet.cssText
        except Exception:
            # Fallback to regex
            return self._rewrite_css_urls_fallback(css_text, css_url)

    def _rewrite_css_url_value(self, value: str, base_url: str) -> str:
        def repl(match):
            raw = match.group(1) or match.group(2)
            url = raw.strip().strip("'\"").strip()
            if not url or url.startswith("data:"):
                return match.group(0)
            full = normalize_url(url, base_url)
            local = self.asset_map.get(full)
            if local:
                return f"url('../{local}')"
            return match.group(0)

        return re.sub(r'url\(\s*(["\']?)([^\)"\']+)\1\s*\)', repl, value)

    def _rewrite_css_urls_fallback(self, css_text: str, base_url: str) -> str:
        def repl(match):
            raw = match.group(1) or match.group(2)
            url = raw.strip().strip("'\"").strip()
            if not url or url.startswith("data:"):
                return match.group(0)
            full = normalize_url(url, base_url)
            local = self.asset_map.get(full)
            if local:
                return f"url('../{local}')"
            return match.group(0)

        return re.sub(r'url\(\s*(["\']?)([^\)"\']+)\1\s*\)', repl, css_text)

    def _to_local_asset(self, value: str, page_url: str) -> str:
        value = value.strip()
        if not value or value.startswith("data:") or value.startswith("#"):
            return value
        if value.startswith("//"):
            value = f"https:{value}"
        full = normalize_url(value, page_url)
        local = self.asset_map.get(full)
        if local:
            # Pages live in pages/, assets live at project root under assets/.
            return f"../{local}"
        # External / broken asset -> remove
        if full.startswith("http") and not self._is_internal(full):
            return ""
        return value

    def _rewrite_srcset(self, srcset: str, page_url: str) -> str:
        parts = []
        for item in srcset.split(","):
            pieces = item.strip().split(" ")
            if not pieces:
                continue
            url = pieces[0]
            local = self._to_local_asset(url, page_url)
            if local:
                parts.append(" ".join([local] + pieces[1:]))
        return ", ".join(parts)

    def _is_internal(self, url: str) -> bool:
        if url.startswith("/") and not url.startswith("//"):
            return True
        if url.startswith("#") or url.startswith("mailto:") or url.startswith("tel:"):
            return False
        parsed = urlparse(url)
        return parsed.netloc.lower() == self.base_parsed.netloc.lower()

    def _to_local_page(self, url: str, page_url: str) -> str:
        full = normalize_url(url, page_url)
        parsed = urlparse(full)
        path = parsed.path.strip("/") or "index"
        if not Path(path).suffix:
            path += ".html"
        # Flatten full path to a unique filename to match export_service
        filename = path.replace("/", "_")
        filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
        return filename + (f"?{parsed.query}" if parsed.query else "")

    def _sanitize_tracking(self, soup: BeautifulSoup):
        tracking_keywords = [
            "google-analytics", "googletagmanager", "gtm-", "analytics", "segment",
            "mixpanel", "hotjar", "hubspot", "intercom", "facebook", "pixel",
            "clarity", "plausible", "matomo", "amplitude", "fullstory",
        ]
        for script in soup.find_all("script"):
            src = (script.get("src") or "").lower()
            text = script.get_text().lower()
            if any(k in src or k in text for k in tracking_keywords):
                script.decompose()
        for tag in soup.find_all("noscript"):
            text = tag.get_text().lower()
            if any(k in text for k in tracking_keywords):
                tag.decompose()

    def _replace_text_nodes(self, soup: BeautifulSoup):
        for elem in soup.find_all(string=True):
            if isinstance(elem, Comment):
                continue
            parent = elem.parent
            if parent and parent.name in ("script", "style", "code", "pre"):
                continue
            new_text = self._apply_replacements(str(elem))
            if new_text != str(elem):
                elem.replace_with(new_text)

    def _apply_replacements(self, text: str) -> str:
        for pattern, placeholder in self.placeholder_patterns:
            text = pattern.sub(placeholder, text)
        return text
