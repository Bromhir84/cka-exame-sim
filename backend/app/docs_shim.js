/*
 * Runs inside proxied documentation pages.
 *
 * kubernetes.io search does `document.location = data-search-page + "?q=" + query`
 * with data-search-page="/search/". The docs iframe is same-origin with the exam
 * app, so that becomes the exam UI (the SPA fallback) instead of search results.
 * Result links are also root-relative ("/docs/..."), which hit the same fallback.
 * This script keeps those navigations on the docs proxy.
 */
(function () {
  var script = document.currentScript;
  var DOC_URL =
    (script && script.getAttribute("data-doc-url")) ||
    "https://kubernetes.io/docs/home/";
  var MSG = "cka-docs-nav";

  function proxyHref(abs) {
    return "/api/docs/proxy?url=" + encodeURIComponent(abs);
  }

  function go(abs) {
    var proxied = proxyHref(abs);
    if (window.parent && window.parent !== window) {
      try {
        window.parent.postMessage(
          { type: MSG, url: abs },
          window.location.origin
        );
      } catch (e) {
        /* parent unavailable */
      }
      // If the exam shell doesn't move the frame, navigate it ourselves.
      window.setTimeout(function () {
        window.location.href = proxied;
      }, 400);
      return;
    }
    window.location.href = proxied;
  }

  function searchDest(page, q) {
    var u = new URL(page || "/search/", DOC_URL);
    if (
      u.origin === window.location.origin &&
      u.pathname.indexOf("/api/docs/proxy") === 0
    ) {
      var inner = u.searchParams.get("url");
      if (inner) u = new URL(inner);
    }
    u.search = "";
    u.hash = "";
    u.searchParams.set("q", q || "");
    return u.href;
  }

  var lastSearch = 0;
  function goSearch(input) {
    var now = Date.now();
    if (now - lastSearch < 500) return;
    lastSearch = now;
    var page = input.getAttribute("data-search-page") || "/search/";
    try {
      go(searchDest(page, input.value || ""));
    } catch (e) {
      /* ignore malformed search targets */
    }
  }

  function searchInput(target) {
    if (!target || !target.closest) return null;
    return target.closest("input[data-search-page], .td-search-input");
  }

  document.addEventListener(
    "keydown",
    function (e) {
      var input = searchInput(e.target);
      if (!input) return;
      if (e.key !== "Enter" && e.keyCode !== 13) return;
      e.preventDefault();
      e.stopImmediatePropagation();
      goSearch(input);
    },
    true
  );

  document.addEventListener(
    "keypress",
    function (e) {
      var input = searchInput(e.target);
      if (!input) return;
      if (e.key !== "Enter" && e.keyCode !== 13) return;
      // The upstream handler assigns location to a root-relative /search/ URL.
      e.preventDefault();
      e.stopImmediatePropagation();
    },
    true
  );

  document.addEventListener(
    "submit",
    function (e) {
      var form = e.target;
      if (!form || !form.querySelector) return;
      var input = form.querySelector(
        "input[data-search-page], .td-search-input"
      );
      if (!input) return;
      e.preventDefault();
      e.stopPropagation();
      goSearch(input);
    },
    true
  );

  document.addEventListener(
    "click",
    function (e) {
      if (e.defaultPrevented) return;
      if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) {
        return;
      }
      var t = e.target;
      if (!t || !t.closest) return;
      var a = t.closest("a[href]");
      if (!a) return;
      var href = a.getAttribute("href");
      if (
        !href ||
        href.charAt(0) === "#" ||
        /^(javascript:|mailto:|data:)/i.test(href)
      ) {
        return;
      }
      var targetAttr = (a.getAttribute("target") || "").toLowerCase();
      var breakout = targetAttr === "_parent" || targetAttr === "_top";
      var resolved;
      try {
        resolved = new URL(href, window.location.href);
      } catch (err) {
        return;
      }
      if (
        !breakout &&
        resolved.origin === window.location.origin &&
        resolved.pathname.indexOf("/api/docs/") === 0
      ) {
        return;
      }

      var dest = null;
      if (resolved.origin === window.location.origin) {
        try {
          dest = new URL(href, DOC_URL).href;
        } catch (err) {
          return;
        }
      } else if (resolved.protocol === "http:" || resolved.protocol === "https:") {
        dest = resolved.href;
      } else {
        return;
      }

      try {
        if (new URL(dest).origin === window.location.origin) return;
      } catch (err) {
        return;
      }

      e.preventDefault();
      e.stopPropagation();
      go(dest);
    },
    true
  );

  // Pagefind and Google CSE read ?q= from this frame's location. The proxy URL
  // keeps the real query inside the `url` parameter, so copy it out before
  // those scripts run.
  try {
    var outer = new URL(window.location.href);
    var raw = outer.searchParams.get("url");
    if (raw) {
      var inner = new URL(raw);
      var changed = false;
      inner.searchParams.forEach(function (v, k) {
        if (k !== "url" && !outer.searchParams.has(k)) {
          outer.searchParams.append(k, v);
          changed = true;
        }
      });
      if (changed) {
        history.replaceState(
          null,
          "",
          outer.pathname + "?" + outer.searchParams.toString() + outer.hash
        );
      }
    }
  } catch (e) {
    /* location isn't a proxied docs URL */
  }
})();
