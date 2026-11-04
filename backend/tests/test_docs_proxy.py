"""Docs browser rewrites: search must not escape onto the exam origin."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.docs_proxy import (  # noqa: E402
    _absolute_search_page,
    _rewrite_html,
    is_allowed,
    is_allowed_asset,
    path_proxy_for,
    resolve_navigation_url,
    unwrap_search_redirect,
)


HOME = "https://kubernetes.io/docs/home/"
SAMPLE = """<!DOCTYPE html>
<html><head><title>Docs</title></head>
<body>
  <form class="td-sidebar__search">
    <input type="search" class="td-search-input" data-search-page="/search/" />
  </form>
  <a href="/docs/concepts/overview/" target="_parent">Overview</a>
  <script src="/pagefind/pagefind-ui.js"></script>
  <script src="/js/main.js"></script>
  <gcse:searchresults-only linktarget="_parent"></gcse:searchresults-only>
</body></html>
"""


class DocsSearchRewriteTests(unittest.TestCase):
    def test_search_page_becomes_absolute_docs_url(self):
        page = _absolute_search_page("/search/", HOME)
        self.assertEqual(page, "https://kubernetes.io/search/")
        # The upstream script concatenates "?q=" + query. That must stay on
        # kubernetes.io, not become a root-relative exam route.
        landed = page + "?q=pods"
        self.assertTrue(landed.startswith("https://kubernetes.io/search/"))
        self.assertNotIn("/api/", landed.split("?", 1)[0])

    def test_localized_search_page(self):
        page = _absolute_search_page(
            "/zh-cn/search/",
            "https://kubernetes.io/zh-cn/docs/home/",
        )
        self.assertEqual(page, "https://kubernetes.io/zh-cn/search/")

    def test_rewritten_html_keeps_search_off_exam_origin(self):
        html = _rewrite_html(SAMPLE, HOME)
        self.assertIn('data-search-page="https://kubernetes.io/search/"', html)
        self.assertNotIn('data-search-page="/search/"', html)
        self.assertIn('src="/api/docs/shim.js"', html)
        self.assertIn(f'data-doc-url="{HOME}"', html)
        self.assertIn('target="_self"', html)
        self.assertIn('linktarget="_self"', html)
        self.assertNotIn('target="_parent"', html)
        self.assertNotIn('linktarget="_parent"', html)
        self.assertIn(
            'src="/api/docs/p/https/kubernetes.io/pagefind/pagefind-ui.js"',
            html,
        )
        self.assertIn("/api/docs/proxy?url=", html)
        self.assertIn("main.js", html)

    def test_pagefind_allowlist(self):
        meta = "https://kubernetes.io/pagefind/pagefind.en.pf_meta"
        wasm = "https://kubernetes.io/pagefind/wasm.en.pagefind"
        self.assertTrue(is_allowed(meta))
        self.assertTrue(is_allowed_asset(meta))
        self.assertTrue(is_allowed_asset(wasm))
        self.assertFalse(is_allowed("https://evil.example/pagefind/pagefind.js"))
        self.assertEqual(
            path_proxy_for("https://kubernetes.io/pagefind/pagefind-ui.js"),
            "/api/docs/p/https/kubernetes.io/pagefind/pagefind-ui.js",
        )

    def test_search_url_stays_allowed(self):
        self.assertTrue(is_allowed("https://kubernetes.io/search/?q=pods"))
        self.assertTrue(is_allowed("https://kubernetes.io/zh-cn/search/?q=pod"))

    def test_google_cse_result_unwraps_to_docs(self):
        # The link shape Google CSE injects into kubernetes.io search results.
        raw = (
            "https://www.google.com/url?client=internal-element-cse"
            "&cx=013288817511911618469:elfqqbqldzg&opi=88066884"
            "&q=https://kubernetes.io/docs/concepts/policy/resource-quotas/"
            "&sa=U&ved=2ahUKEwin76jL_-2XAxUNXUEAHdycFaYQFnoECAUQAg"
            "&usg=AOvVaw04ARryruBdoNd0gx7EsEB4"
        )
        docs = "https://kubernetes.io/docs/concepts/policy/resource-quotas/"
        self.assertEqual(unwrap_search_redirect(raw), docs)
        self.assertEqual(resolve_navigation_url(raw), docs)
        self.assertTrue(is_allowed(docs))
        self.assertFalse(is_allowed(raw))

    def test_google_cse_url_param_and_non_redirects(self):
        encoded = (
            "https://www.google.com/url?q=&sa=U&url="
            "https%3A%2F%2Fhelm.sh%2Fdocs%2F"
        )
        self.assertEqual(
            unwrap_search_redirect(encoded),
            "https://helm.sh/docs/",
        )
        search = "https://www.google.com/search?q=pods"
        self.assertEqual(unwrap_search_redirect(search), search)
        self.assertFalse(is_allowed(search))


if __name__ == "__main__":
    unittest.main()
