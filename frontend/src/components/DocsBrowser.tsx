import { FormEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";

type Bookmark = { title: string; url: string };

function proxySrc(url: string): string {
  return `/api/docs/proxy?url=${encodeURIComponent(url)}`;
}

export default function DocsBrowser() {
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [currentUrl, setCurrentUrl] = useState(
    "https://kubernetes.io/docs/home/"
  );
  const [address, setAddress] = useState(currentUrl);
  const [history, setHistory] = useState<string[]>([currentUrl]);
  const [histIndex, setHistIndex] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const frameRef = useRef<HTMLIFrameElement>(null);
  const historyRef = useRef(history);
  const histIndexRef = useRef(histIndex);
  const currentUrlRef = useRef(currentUrl);
  historyRef.current = history;
  histIndexRef.current = histIndex;
  currentUrlRef.current = currentUrl;

  const navigateTo = useCallback((url: string, push = true) => {
    setError(null);
    let next = url.trim();
    if (!/^https?:\/\//i.test(next)) {
      next = `https://${next}`;
    }
    setAddress(next);
    if (next === currentUrlRef.current) return;
    currentUrlRef.current = next;
    setCurrentUrl(next);
    if (!push) return;
    const trimmed = historyRef.current.slice(0, histIndexRef.current + 1);
    if (trimmed[trimmed.length - 1] !== next) trimmed.push(next);
    const idx = trimmed.length - 1;
    historyRef.current = trimmed;
    histIndexRef.current = idx;
    setHistory(trimmed);
    setHistIndex(idx);
  }, []);

  useEffect(() => {
    fetch("/api/docs/bookmarks")
      .then((r) => r.json())
      .then((data) => {
        setBookmarks(data.bookmarks || []);
        if (data.default_url) {
          currentUrlRef.current = data.default_url;
          histIndexRef.current = 0;
          historyRef.current = [data.default_url];
          setCurrentUrl(data.default_url);
          setAddress(data.default_url);
          setHistory([data.default_url]);
          setHistIndex(0);
        }
      })
      .catch(() => {
        /* bookmarks optional at runtime */
      });
  }, []);

  // In-page search and result clicks ask the shell to move the iframe. A
  // root-relative /search/ navigation would otherwise load this exam UI.
  useEffect(() => {
    const onMsg = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) return;
      const data = event.data;
      if (!data || data.type !== "cka-docs-nav" || typeof data.url !== "string") {
        return;
      }
      const frame = frameRef.current;
      if (frame && event.source !== frame.contentWindow) return;
      navigateTo(data.url);
    };
    window.addEventListener("message", onMsg);
    return () => window.removeEventListener("message", onMsg);
  }, [navigateTo]);

  const iframeSrc = useMemo(() => proxySrc(currentUrl), [currentUrl]);

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    navigateTo(address);
  };

  const goBack = () => {
    if (histIndex <= 0) return;
    const idx = histIndex - 1;
    const url = history[idx];
    histIndexRef.current = idx;
    currentUrlRef.current = url;
    setHistIndex(idx);
    setCurrentUrl(url);
    setAddress(url);
  };

  const goForward = () => {
    if (histIndex >= history.length - 1) return;
    const idx = histIndex + 1;
    const url = history[idx];
    histIndexRef.current = idx;
    currentUrlRef.current = url;
    setHistIndex(idx);
    setCurrentUrl(url);
    setAddress(url);
  };

  return (
    <div className="docs-browser">
      <div className="docs-toolbar">
        <button type="button" className="btn" onClick={goBack} disabled={histIndex <= 0}>
          ←
        </button>
        <button
          type="button"
          className="btn"
          onClick={goForward}
          disabled={histIndex >= history.length - 1}
        >
          →
        </button>
        <form className="docs-address" onSubmit={onSubmit}>
          <input
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            spellCheck={false}
            aria-label="Docs URL"
            placeholder="https://kubernetes.io/docs/..."
          />
          <button type="submit" className="btn primary">
            Go
          </button>
        </form>
      </div>
      <div className="docs-bookmarks">
        {bookmarks.map((b) => (
          <button
            key={b.url}
            type="button"
            className="docs-bookmark"
            onClick={() => navigateTo(b.url)}
            title={b.url}
          >
            {b.title}
          </button>
        ))}
      </div>
      {error && <div className="docs-error">{error}</div>}
      <iframe
        ref={frameRef}
        className="docs-frame"
        title="Exam documentation browser"
        src={iframeSrc}
        sandbox="allow-same-origin allow-scripts allow-forms allow-popups"
        onError={() => setError("Failed to load page")}
      />
    </div>
  );
}
