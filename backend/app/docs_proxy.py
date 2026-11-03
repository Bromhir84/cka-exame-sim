from __future__ import annotations

import re
from urllib.parse import quote, urljoin, urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

# Align with typical CKA PSI allowlist (docs + kubernetes GitHub org).
ALLOWED_PREFIXES = (
    "https://kubernetes.io/docs/",
    "https://kubernetes.io/blog/",
    "https://kubernetes.io/search/",
    "https://kubernetes.io/css/",
    "https://kubernetes.io/js/",
    "https://kubernetes.io/images/",
    "https://kubernetes.io/fonts/",
    "https://kubernetes.io/static/",
    "https://github.com/kubernetes/",
    "https://github.com/kubernetes-sigs/",
    "https://raw.githubusercontent.com/kubernetes/",
    "https://raw.githubusercontent.com/kubernetes-sigs/",
)

# Static assets sometimes load from these hosts while reading docs.
ALLOWED_ASSET_HOSTS = {
    "kubernetes.io",
    "www.kubernetes.io",
    "github.com",
    "raw.githubusercontent.com",
    "avatars.githubusercontent.com",
    "camo.githubusercontent.com",
    "cdnjs.cloudflare.com",
    "fonts.googleapis.com",
    "fonts.gstatic.com",
}

BOOKMARKS = [
    {
        "title": "Kubernetes Docs",
        "url": "https://kubernetes.io/docs/home/",
    },
    {
        "title": "kubectl Reference",
        "url": "https://kubernetes.io/docs/reference/kubectl/",
    },
    {
        "title": "kubectl Cheat Sheet",
        "url": "https://kubernetes.io/docs/reference/kubectl/quick-reference/",
    },
    {
        "title": "API Reference",
        "url": "https://kubernetes.io/docs/reference/kubernetes-api/",
    },
    {
        "title": "kubernetes/kubernetes (GitHub)",
        "url": "https://github.com/kubernetes/kubernetes",
    },
    {
        "title": "kubernetes/website (GitHub)",
        "url": "https://github.com/kubernetes/website",
    },
]

DEFAULT_URL = BOOKMARKS[0]["url"]

router = APIRouter(prefix="/api/docs", tags=["docs"])


def _normalize(url: str) -> str:
    url = url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="url required")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="only http(s) URLs allowed")
    # Force https for known hosts
    if parsed.scheme == "http" and parsed.netloc in ALLOWED_ASSET_HOSTS:
        url = urlunparse(("https", parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
    return url


def is_allowed(url: str) -> bool:
    try:
        url = _normalize(url)
    except HTTPException:
        return False
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
        url = urlunparse((parsed.scheme, host, parsed.path, parsed.params, parsed.query, parsed.fragment))
        parsed = urlparse(url)

    # Exact prefix allow for navigation targets
    for prefix in ALLOWED_PREFIXES:
        if url.startswith(prefix) or url.rstrip("/") == prefix.rstrip("/"):
            return True

    path = parsed.path or "/"

    if host == "github.com":
        return path.startswith("/kubernetes/") or path.startswith("/kubernetes-sigs/")

    if host == "raw.githubusercontent.com":
        return path.startswith("/kubernetes/") or path.startswith("/kubernetes-sigs/")

    if host in {"avatars.githubusercontent.com", "camo.githubusercontent.com"}:
        return True

    if host in {"cdnjs.cloudflare.com", "fonts.googleapis.com", "fonts.gstatic.com"}:
        return True

    # kubernetes.io static assets only (navigation must match ALLOWED_PREFIXES above)
    if host in {"kubernetes.io", "www.kubernetes.io"} or host.endswith(".kubernetes.io"):
        asset_prefixes = ("/css/", "/js/", "/images/", "/fonts/", "/static/", "/icons/")
        return path.startswith(asset_prefixes)

    return False


def proxy_url_for(target: str) -> str:
    return f"/api/docs/proxy?url={quote(target, safe='')}"


def _rewrite_html(html: str, base_url: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Remove frame-busting / CSP meta
    for tag in soup.find_all("meta"):
        http_equiv = (tag.get("http-equiv") or "").lower()
        if http_equiv in {"content-security-policy", "x-frame-options"}:
            tag.decompose()

    for tag in soup.find_all(["a", "link", "script", "img", "iframe", "form", "source"]):
        for attr in ("href", "src", "action"):
            val = tag.get(attr)
            if not val or val.startswith(("data:", "mailto:", "javascript:", "#")):
                continue
            absolute = urljoin(base_url, val)
            if is_allowed(absolute):
                tag[attr] = proxy_url_for(absolute)
            else:
                # Neutralize disallowed navigation
                if attr == "href":
                    tag[attr] = "#"
                    tag["title"] = "Blocked: outside exam allowlist"
                    tag["data-blocked"] = "1"
                elif attr in ("src", "action"):
                    tag[attr] = ""

    # Inject small banner note
    notice = soup.new_tag("div")
    notice.attrs["style"] = (
        "position:sticky;top:0;z-index:99999;background:#1a212b;color:#e8eef5;"
        "padding:6px 10px;font:12px/1.4 sans-serif;border-bottom:1px solid #2a3544;"
    )
    notice.string = "Exam docs browser — navigation limited to allowed Kubernetes resources."
    if soup.body:
        soup.body.insert(0, notice)
    elif soup.html:
        soup.html.insert(0, notice)

    return str(soup)


@router.get("/bookmarks")
async def docs_bookmarks():
    return {"bookmarks": BOOKMARKS, "default_url": DEFAULT_URL}


@router.get("/proxy")
async def docs_proxy(url: str = Query(..., min_length=8)):
    target = _normalize(url)
    if not is_allowed(target):
        raise HTTPException(
            status_code=403,
            detail="URL is not on the exam allowlist (kubernetes.io docs/blog and kubernetes GitHub only).",
        )

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0,
            headers={
                "User-Agent": "CKA-Exam-Simulator-DocsBrowser/1.0",
                "Accept": "*/*",
            },
        ) as client:
            upstream = await client.get(target)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"upstream fetch failed: {exc}") from exc

    # If redirect chain left allowlist, block
    final_url = str(upstream.url)
    if not is_allowed(final_url):
        raise HTTPException(status_code=403, detail="Redirect target is not allowlisted")

    content_type = upstream.headers.get("content-type", "application/octet-stream")
    body = upstream.content

    if "text/html" in content_type.lower():
        try:
            text = body.decode(upstream.charset_encoding or "utf-8", errors="replace")
        except LookupError:
            text = body.decode("utf-8", errors="replace")
        text = _rewrite_html(text, final_url)
        # Soften base paths
        text = re.sub(
            r'<meta[^>]+http-equiv=["\']?content-security-policy["\']?[^>]*>',
            "",
            text,
            flags=re.I,
        )
        return Response(
            content=text,
            media_type="text/html; charset=utf-8",
            headers={
                "Cache-Control": "private, max-age=60",
                "X-Frame-Options": "SAMEORIGIN",
            },
        )

    return Response(
        content=body,
        media_type=content_type,
        headers={"Cache-Control": "private, max-age=300"},
    )
