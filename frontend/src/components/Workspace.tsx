import { useState } from "react";
import DocsBrowser from "./DocsBrowser";
import Terminal from "./Terminal";

type Props = {
  sessionId: string;
  active: boolean;
};

export default function Workspace({ sessionId, active }: Props) {
  const [tab, setTab] = useState<"terminal" | "docs">("terminal");

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
      </div>
    </div>
  );
}
