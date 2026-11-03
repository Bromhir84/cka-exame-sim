import { useEffect, useRef } from "react";
import { Terminal as XTerm } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import "@xterm/xterm/css/xterm.css";
import { terminalWsUrl } from "../api";

type Props = {
  sessionId: string;
  active: boolean;
};

export default function Terminal({ sessionId, active }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const termRef = useRef<XTerm | null>(null);

  useEffect(() => {
    if (!active || !containerRef.current) return;

    const term = new XTerm({
      cursorBlink: true,
      fontFamily: '"IBM Plex Mono", ui-monospace, monospace',
      fontSize: 14,
      theme: {
        background: "#0f1419",
        foreground: "#e7ecf1",
        cursor: "#7dd3c0",
        selectionBackground: "#2a3a4a",
      },
    });
    const fit = new FitAddon();
    term.loadAddon(fit);
    term.open(containerRef.current);
    fit.fit();
    termRef.current = term;

    const ws = new WebSocket(terminalWsUrl(sessionId));
    ws.binaryType = "arraybuffer";

    ws.onopen = () => {
      const dims = fit.proposeDimensions();
      if (dims) {
        ws.send(`resize:${dims.cols}x${dims.rows}`);
      }
      term.focus();
    };

    ws.onmessage = (ev) => {
      if (typeof ev.data === "string") {
        term.write(ev.data);
      } else {
        term.write(new Uint8Array(ev.data as ArrayBuffer));
      }
    };

    ws.onclose = () => {
      term.writeln("\r\n\x1b[33m[terminal disconnected]\x1b[0m");
    };

    term.onData((data) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(data);
      }
    });

    const onResize = () => {
      fit.fit();
      const dims = fit.proposeDimensions();
      if (dims && ws.readyState === WebSocket.OPEN) {
        ws.send(`resize:${dims.cols}x${dims.rows}`);
      }
    };
    window.addEventListener("resize", onResize);
    const ro = new ResizeObserver(onResize);
    ro.observe(containerRef.current);

    return () => {
      window.removeEventListener("resize", onResize);
      ro.disconnect();
      ws.close();
      term.dispose();
      termRef.current = null;
    };
  }, [sessionId, active]);

  return <div className="terminal" ref={containerRef} />;
}
