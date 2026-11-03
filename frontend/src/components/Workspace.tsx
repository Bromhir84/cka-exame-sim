import { useState } from "react";
import DocsBrowser from "./DocsBrowser";
import Terminal from "./Terminal";

type Props = {
  sessionId: string;
  active: boolean;
  desktopUrl?: string | null;
  desktopError?: string | null;
};

export default function Workspace({
  sessionId,
  active,
  desktopUrl,
  desktopError,
}: Props) {
  const [tab, setTab] = useState<"terminal" | "docs" | "desktop">("terminal");

  return (
    <div className="workspace">
      <div className="workspace-tabs" role="tablist">
        <button
          type="button"
          role="tab"
          aria-selected={tab === "terminal"}
          className={tab === "terminal" ? "active" : ""}
          onClick={() => setTab("terminal")}
        >
          Terminal
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === "docs"}
          className={tab === "docs" ? "active" : ""}
          onClick={() => setTab("docs")}
        >
          Docs
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === "desktop"}
          className={tab === "desktop" ? "active" : ""}
          onClick={() => setTab("desktop")}
          title={
            desktopUrl
              ? "Remote desktop (noVNC)"
              : desktopError || "Desktop unavailable"
          }
        >
          Desktop
        </button>
      </div>
      <div className="workspace-body">
        {/* Keep terminal mounted so the PTY/WebSocket stays alive across tab switches */}
        <div
          className={
            tab === "terminal" ? "workspace-pane active" : "workspace-pane"
          }
          hidden={tab !== "terminal"}
        >
          <Terminal sessionId={sessionId} active={active} />
        </div>
        <div
          className={tab === "docs" ? "workspace-pane active" : "workspace-pane"}
          hidden={tab !== "docs"}
        >
          {active ? <DocsBrowser /> : null}
        </div>
        <div
          className={
            tab === "desktop" ? "workspace-pane active" : "workspace-pane"
          }
          hidden={tab !== "desktop"}
        >
          {desktopUrl ? (
            <iframe
              className="desktop-frame"
              title="Exam desktop"
              src={desktopUrl}
              allow="clipboard-read; clipboard-write"
            />
          ) : (
            <div className="desktop-missing">
              <p>Remote desktop is not available for this session.</p>
              {desktopError ? (
                <pre className="desktop-error">{desktopError}</pre>
              ) : (
                <p>
                  Use Terminal and Docs instead. If this persists after a
                  rebuild, check that the <code>cka-exame-sim-desktop</code>{" "}
                  image built successfully.
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
