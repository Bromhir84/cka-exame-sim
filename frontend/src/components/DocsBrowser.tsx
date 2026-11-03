import { FormEvent, useEffect, useMemo, useState } from "react";

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

  useEffect(() => {
    fetch("/api/docs/bookmarks")
      .then((r) => r.json())
      .then((data) => {
        setBookmarks(data.bookmarks || []);
        if (data.default_url) {
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

  const iframeSrc = useMemo(() => proxySrc(currentUrl), [currentUrl]);

  const navigateTo = (url: string, push = true) => {
    setError(null);
    let next = url.trim();
    if (!/^https?:\/\//i.test(next)) {
      next = `https://${next}`;
    }
    setCurrentUrl(next);
    setAddress(next);
    if (push) {
      setHistory((prev) => {
        const trimmed = prev.slice(0, histIndex + 1);
        trimmed.push(next);
        setHistIndex(trimmed.length - 1);
        return trimmed;
      });
    }
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    navigateTo(address);
  };

  const goBack = () => {
    if (histIndex <= 0) return;
    const idx = histIndex - 1;
    setHistIndex(idx);
    const url = history[idx];
    setCurrentUrl(url);
    setAddress(url);
  };

  const goForward = () => {
    if (histIndex >= history.length - 1) return;
    const idx = histIndex + 1;
    setHistIndex(idx);
    const url = history[idx];
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
        className="docs-frame"
        title="Exam documentation browser"
        src={iframeSrc}
        sandbox="allow-same-origin allow-scripts allow-forms allow-popups"
        onError={() => setError("Failed to load page")}
      />
    </div>
  );
}
