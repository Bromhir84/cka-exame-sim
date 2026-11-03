from __future__ import annotations

import re
from urllib.parse import quote, urljoin, urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

# Official CKA browser allowlist (Linux Foundation “Resources Allowed”):
# https://docs.linuxfoundation.org/tc-docs/certification/certification-resources-allowed
# - https://kubernetes.io/docs (+ translations)
# - https://kubernetes.io/blog
# - https://helm.sh/docs
# - https://gateway-api.sigs.k8s.io (CKA only)
# Search on kubernetes.io/docs is allowed; only open results on the domains above.
# Task Quick Reference may add extra links for a specific item — not free browsing.
ALLOWED_PREFIXES = (
    "https://kubernetes.io/docs/",
    "https://kubernetes.io/blog/",
    "https://kubernetes.io/search/",
    "https://kubernetes.io/css/",
    "https://kubernetes.io/scss/",
    "https://kubernetes.io/js/",
    "https://kubernetes.io/images/",
    "https://kubernetes.io/fonts/",
    "https://kubernetes.io/static/",
    "https://kubernetes.io/icons/",
    "https://helm.sh/docs/",
    "https://gateway-api.sigs.k8s.io/",
)

# Hosts that may serve styles/scripts/images for allowlisted pages.
ALLOWED_ASSET_HOSTS = {
    "kubernetes.io",
    "www.kubernetes.io",
    "helm.sh",
    "www.helm.sh",
    "gateway-api.sigs.k8s.io",
    "k8s.io",
    "www.k8s.io",
    "cdnjs.cloudflare.com",
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "code.jquery.com",
    # GitHub asset CDNs appear on some doc sites / quick-ref targets
    "avatars.githubusercontent.com",
    "camo.githubusercontent.com",
    "user-images.githubusercontent.com",
    "github.githubassets.com",
    "opengraph.githubassets.com",
}

_K8S_ASSET_PREFIXES = (
    "/css/",
    "/scss/",
    "/sass/",
    "/js/",
    "/images/",
    "/fonts/",
    "/static/",
    "/icons/",
    "/assets/",
    "/dist/",
)
_ASSET_EXTENSIONS = (
    ".css",
    ".js",
    ".mjs",
    ".map",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".otf",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".ico",
    ".webmanifest",
)

# Locale + docs/blog/search on kubernetes.io (e.g. /zh-cn/docs/...)
_K8S_NAV_PATH = re.compile(
    r"^/(?:[a-z]{2}(?:-[a-z0-9]+)?/)?(?:docs|blog|search)(?:/|$)",
    re.I,
)
_CSS_URL_RE = re.compile(r"url\(\s*([\"']?)([^\"')]+)\1\s*\)", re.I)

BOOKMARKS = [
    {
        "title": "Kubernetes Docs",
        "url": "https://kubernetes.io/docs/home/",
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
        "title": "Kubernetes Blog",
        "url": "https://kubernetes.io/blog/",
    },
    {
        "title": "Helm Docs",
        "url": "https://helm.sh/docs/",
    },
    {
        "title": "Gateway API (CKA)",
        "url": "https://gateway-api.sigs.k8s.io/",
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
    host = parsed.netloc.lower()
    if parsed.scheme == "http" and (
        host in ALLOWED_ASSET_HOSTS
        or host.endswith(".kubernetes.io")
        or host.endswith(".sigs.k8s.io")
        or host.endswith(".helm.sh")
        or host.endswith(".githubassets.com")
        or host.endswith(".githubusercontent.com")
    ):
        url = urlunparse(
            ("https", parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment)
        )
    return url


def _strip_www(url: str) -> tuple[str, str, str]:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
        url = urlunparse(
            (parsed.scheme, host, parsed.path, parsed.params, parsed.query, parsed.fragment)
        )
        parsed = urlparse(url)
    return url, host, parsed.path or "/"


def _looks_like_asset(path: str) -> bool:
    lower = path.lower()
    if any(lower.startswith(p) for p in _K8S_ASSET_PREFIXES):
        return True
    # Strip query-less path extension
    clean = lower.split("?", 1)[0]
    return any(clean.endswith(ext) for ext in _ASSET_EXTENSIONS)


def is_allowed_asset(url: str) -> bool:
    """Styles, scripts, images, fonts needed to render allowlisted pages."""
    try:
        url = _normalize(url)
    except HTTPException:
        return False
    url, host, path = _strip_www(url)

    if host in ALLOWED_ASSET_HOSTS:
        # Entire CDN / doc-site hosts used only for rendering
        if host not in {"kubernetes.io", "helm.sh", "gateway-api.sigs.k8s.io", "k8s.io"}:
            return True

    if host.endswith(".githubassets.com") or host.endswith(".githubusercontent.com"):
        return True

    if host in {"kubernetes.io"} or host.endswith(".kubernetes.io"):
        return _looks_like_asset(path) or bool(_K8S_NAV_PATH.match(path))

    if host in {"helm.sh", "www.helm.sh"} or host.endswith(".helm.sh"):
        return path.startswith("/docs/") or _looks_like_asset(path)

    if host == "gateway-api.sigs.k8s.io" or host.endswith(".sigs.k8s.io"):
        # Gateway API site + static assets under sigs.k8s.io for that doc set
        return host == "gateway-api.sigs.k8s.io" or _looks_like_asset(path)

    if host in {"k8s.io", "www.k8s.io"}:
        # Short links / static helpers that resolve into docs
        return True

    return False


def is_allowed(url: str) -> bool:
    """Navigation targets allowed on the real CKA (plus required static assets)."""
    try:
        url = _normalize(url)
    except HTTPException:
        return False
    url, host, path = _strip_www(url)

    for prefix in ALLOWED_PREFIXES:
        if url.startswith(prefix) or url.rstrip("/") == prefix.rstrip("/"):
            return True

    # Versioned docs hosts (v1-34.docs.kubernetes.io, etc.)
    if host.endswith(".docs.kubernetes.io") or host == "docs.kubernetes.io":
        return True

    if host == "kubernetes.io":
        if _K8S_NAV_PATH.match(path):
            return True
        return _looks_like_asset(path)

    if host.endswith(".kubernetes.io") and _looks_like_asset(path):
        return True

    # Helm docs (CKA/CKAD)
    if host in {"helm.sh", "www.helm.sh"}:
        return path.startswith("/docs/") or path.rstrip("/") == "/docs" or _looks_like_asset(
            path
        )

    # Gateway API docs (CKA only on the real exam)
    if host == "gateway-api.sigs.k8s.io":
        return True

    # k8s.io short links often redirect into kubernetes.io docs
    if host in {"k8s.io", "www.k8s.io"}:
        return True

    return False


def proxy_url_for(target: str) -> str:
    return f"/api/docs/proxy?url={quote(target, safe='')}"


def blocked_url_for(target: str) -> str:
    return f"/api/docs/blocked?url={quote(target, safe='')}"


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def blocked_page_html(requested_url: str, reason: str | None = None) -> str:
    """Exam-style interstitial when a URL is outside the allowlist."""
    safe_url = _esc(requested_url or "(empty)")
    safe_reason = _esc(
        reason
        or "This exam browser matches the real CKA allowlist: kubernetes.io docs/blog, helm.sh/docs, and gateway-api.sigs.k8s.io."
    )
    links = "\n".join(
        (
            f'      <li><a href="{_esc(proxy_url_for(b["url"]))}">'
            f'{_esc(b["title"])}</a>'
            f'<span class="u">{_esc(b["url"])}</span></li>'
        )
        for b in BOOKMARKS
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Site not allowed — CKA exam browser</title>
  <style>
    :root {{
      --bg: #0f1419;
      --panel: #161d27;
      --line: #2a3544;
      --text: #e8eef5;
      --muted: #9aa8b8;
      --accent: #3d8bfd;
      --warn: #f0b429;
      --warn-bg: #2a2110;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: "Segoe UI", system-ui, sans-serif;
      background:
        radial-gradient(ellipse 80% 50% at 50% -10%, #1c2a3d 0%, transparent 55%),
        var(--bg);
      color: var(--text);
      display: grid;
      place-items: center;
      padding: 2rem 1.25rem;
    }}
    .card {{
      width: min(36rem, 100%);
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 0.75rem;
      padding: 1.75rem 1.5rem 1.5rem;
      box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
    }}
    .badge {{
      display: inline-block;
      font-size: 0.72rem;
      font-weight: 650;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--warn);
      background: var(--warn-bg);
      border: 1px solid #5c4a1e;
      border-radius: 999px;
      padding: 0.25rem 0.65rem;
      margin-bottom: 0.85rem;
    }}
    h1 {{
      margin: 0 0 0.5rem;
      font-size: 1.45rem;
      font-weight: 650;
      letter-spacing: -0.02em;
    }}
    .lead {{
      margin: 0 0 1.15rem;
      color: var(--muted);
      line-height: 1.5;
      font-size: 0.95rem;
    }}
    .url-box {{
      background: #0c1015;
      border: 1px solid var(--line);
      border-radius: 0.45rem;
      padding: 0.75rem 0.85rem;
      margin-bottom: 1.25rem;
    }}
    .url-box .label {{
      display: block;
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--muted);
      margin-bottom: 0.35rem;
    }}
    .url-box code {{
      display: block;
      font-family: ui-monospace, "Cascadia Code", Consolas, monospace;
      font-size: 0.82rem;
      word-break: break-all;
      color: #ffc9cf;
      line-height: 1.4;
    }}
    h2 {{
      margin: 0 0 0.55rem;
      font-size: 0.85rem;
      font-weight: 650;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    ul {{
      list-style: none;
      margin: 0;
      padding: 0;
      display: grid;
      gap: 0.45rem;
    }}
    li {{
      border: 1px solid var(--line);
      border-radius: 0.4rem;
      padding: 0.55rem 0.7rem;
      background: #121820;
    }}
    li a {{
      color: var(--accent);
      font-weight: 600;
      text-decoration: none;
      font-size: 0.92rem;
    }}
    li a:hover {{ text-decoration: underline; }}
    li .u {{
      display: block;
      margin-top: 0.2rem;
      font-size: 0.72rem;
      color: var(--muted);
      font-family: ui-monospace, Consolas, monospace;
      word-break: break-all;
    }}
    .foot {{
      margin: 1.25rem 0 0;
      font-size: 0.8rem;
      color: var(--muted);
      line-height: 1.45;
    }}
  </style>
</head>
<body>
  <main class="card" role="alert">
    <div class="badge">Exam browser</div>
    <h1>This site is not allowed</h1>
    <p class="lead">{safe_reason}</p>
    <div class="url-box">
      <span class="label">Requested URL</span>
      <code>{safe_url}</code>
    </div>
    <h2>Allowed starting points</h2>
    <ul>
{links}
    </ul>
    <p class="foot">
      Allowed on the real CKA: kubernetes.io/docs (and translations), kubernetes.io/blog,
      helm.sh/docs, and gateway-api.sigs.k8s.io. Search is OK on kubernetes.io/docs,
      but do not open off-allowlist search results.
    </p>
  </main>
</body>
</html>
"""


def blocked_response(requested_url: str, reason: str | None = None) -> Response:
    return Response(
        content=blocked_page_html(requested_url, reason),
        status_code=403,
        media_type="text/html; charset=utf-8",
        headers={
            "Cache-Control": "no-store",
            "X-Frame-Options": "SAMEORIGIN",
            "X-Exam-Docs-Blocked": "1",
        },
    )


def _rewrite_css(css: str, base_url: str) -> str:
    def repl(match: re.Match[str]) -> str:
        quote_ch, raw = match.group(1), match.group(2).strip()
        if not raw or raw.startswith("data:") or raw.startswith("#"):
            return match.group(0)
        absolute = urljoin(base_url, raw)
        if is_allowed_asset(absolute) or is_allowed(absolute):
            proxied = proxy_url_for(absolute)
            return f"url({quote_ch}{proxied}{quote_ch})"
        return "url()"

    return _CSS_URL_RE.sub(repl, css)


def _is_navigational_tag(tag) -> bool:
    name = (tag.name or "").lower()
    if name == "a":
        return True
    if name == "form":
        return True
    if name == "link":
        rel = " ".join(tag.get("rel") or []).lower()
        # Stylesheets / icons / preload are assets; alternate/html is navigation-ish
        if any(
            r in rel
            for r in ("stylesheet", "icon", "preload", "prefetch", "modulepreload", "manifest")
        ):
            return False
        return True
    return False


def _rewrite_html(html: str, base_url: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Remove frame-busting / CSP meta (also strip SRI on proxied assets — body is
    # unchanged, but some browsers are picky when the request URL changes).
    for tag in soup.find_all("meta"):
        http_equiv = (tag.get("http-equiv") or "").lower()
        if http_equiv in {"content-security-policy", "x-frame-options"}:
            tag.decompose()

    for tag in soup.find_all(["a", "link", "script", "img", "iframe", "form", "source"]):
        # Integrity checks break once we rewrite URLs through our proxy.
        if tag.has_attr("integrity"):
            del tag["integrity"]
        if tag.has_attr("crossorigin"):
            del tag["crossorigin"]

        for attr in ("href", "src", "action"):
            val = tag.get(attr)
            if not val or val.startswith(("data:", "mailto:", "javascript:", "#")):
                continue
            absolute = urljoin(base_url, val)
            navigational = _is_navigational_tag(tag) and attr in {"href", "action"}

            if navigational:
                if is_allowed(absolute):
                    tag[attr] = proxy_url_for(absolute)
                else:
                    tag[attr] = blocked_url_for(absolute)
                    tag["title"] = "Blocked: outside exam allowlist"
                    tag["data-blocked"] = "1"
                continue

            # Assets: stylesheet, script, image, etc.
            if is_allowed_asset(absolute) or is_allowed(absolute):
                tag[attr] = proxy_url_for(absolute)
            else:
                # Never point CSS/JS at the HTML blocked page (that yields a
                # plain-text looking document). Drop the resource instead.
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


@router.get("/blocked")
async def docs_blocked(url: str = Query(default="", max_length=2048)):
    """HTML interstitial for allowlist violations (also used from rewritten links)."""
    display = url.strip() or "(no URL)"
    return blocked_response(
        display,
        "This exam browser matches the real CKA allowlist: kubernetes.io docs/blog, helm.sh/docs, and gateway-api.sigs.k8s.io.",
    )


@router.get("/proxy")
async def docs_proxy(url: str = Query(..., min_length=8)):
    try:
        target = _normalize(url)
    except HTTPException:
        return blocked_response(
            url,
            "Only http(s) URLs can be opened in the exam docs browser.",
        )
    if not (is_allowed(target) or is_allowed_asset(target)):
        return blocked_response(
            target,
            "This exam browser matches the real CKA allowlist: kubernetes.io docs/blog, helm.sh/docs, and gateway-api.sigs.k8s.io.",
        )

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; CKA-Exam-Simulator-DocsBrowser/1.0)"
                ),
                "Accept": "*/*",
            },
        ) as client:
            upstream = await client.get(target)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"upstream fetch failed: {exc}") from exc

    final_url = str(upstream.url)
    if not (is_allowed(final_url) or is_allowed_asset(final_url)):
        return blocked_response(
            final_url,
            "A redirect left the exam allowlist, so this page was blocked.",
        )

    content_type = upstream.headers.get("content-type", "application/octet-stream")
    body = upstream.content
    ctype_lower = content_type.lower()

    if "text/html" in ctype_lower:
        try:
            text = body.decode(upstream.charset_encoding or "utf-8", errors="replace")
        except LookupError:
            text = body.decode("utf-8", errors="replace")
        text = _rewrite_html(text, final_url)
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

    if "text/css" in ctype_lower or final_url.lower().split("?", 1)[0].endswith(".css"):
        try:
            text = body.decode(upstream.charset_encoding or "utf-8", errors="replace")
        except LookupError:
            text = body.decode("utf-8", errors="replace")
        text = _rewrite_css(text, final_url)
        return Response(
            content=text,
            media_type="text/css; charset=utf-8",
            headers={"Cache-Control": "private, max-age=300"},
        )

    return Response(
        content=body,
        media_type=content_type,
        headers={"Cache-Control": "private, max-age=300"},
    )
