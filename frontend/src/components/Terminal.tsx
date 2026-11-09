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

    let closed = false;
    let connecting = false;
    let announced = false;
    let retry = 0;
    let retryTimer = 0;
    let ws: WebSocket | null = null;

    const sendResize = (socket: WebSocket) => {
      fit.fit();
      const dims = fit.proposeDimensions();
      if (dims && socket.readyState === WebSocket.OPEN) {
        socket.send(`resize:${dims.cols}x${dims.rows}`);
      }
    };

    const connect = () => {
      if (closed || connecting) return;
      if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
        return;
      }
      connecting = true;
      const socket = new WebSocket(terminalWsUrl(sessionId));
      ws = socket;
      socket.binaryType = "arraybuffer";

      socket.onopen = () => {
        connecting = false;
        retry = 0;
        sendResize(socket);
        if (announced) {
          term.writeln("\r\n\x1b[32m[terminal reconnected]\x1b[0m");
          announced = false;
        }
        term.focus();
      };

      socket.onmessage = (ev) => {
        if (typeof ev.data === "string") {
          term.write(ev.data);
        } else {
          term.write(new Uint8Array(ev.data as ArrayBuffer));
        }
      };

      socket.onclose = (ev) => {
        connecting = false;
        if (ws === socket) ws = null;
        if (closed) return;
        // 4404: session is not ready yet. Wait for the page to wake instead of spinning.
        if (ev.code === 4404) return;
        if (!announced) {
          term.writeln("\r\n\x1b[33m[terminal disconnected — reconnecting]\x1b[0m");
          announced = true;
        }
        const delay = Math.min(1000 * 2 ** retry, 8000);
        retry += 1;
        window.clearTimeout(retryTimer);
        retryTimer = window.setTimeout(connect, delay);
      };
    };

    const onData = term.onData((data) => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(data);
      }
    });

    const onResize = () => {
      if (ws && ws.readyState === WebSocket.OPEN) sendResize(ws);
      else fit.fit();
    };
    window.addEventListener("resize", onResize);
    const ro = new ResizeObserver(onResize);
    ro.observe(containerRef.current);

    const wake = () => {
      if (document.visibilityState === "hidden") return;
      if (ws && ws.readyState === WebSocket.OPEN) {
        sendResize(ws);
        return;
      }
      window.clearTimeout(retryTimer);
      retry = 0;
      connect();
    };
    document.addEventListener("visibilitychange", wake);
    window.addEventListener("online", wake);
    window.addEventListener("pageshow", wake);

    connect();

    return () => {
      closed = true;
      window.clearTimeout(retryTimer);
      document.removeEventListener("visibilitychange", wake);
      window.removeEventListener("online", wake);
      window.removeEventListener("pageshow", wake);
      window.removeEventListener("resize", onResize);
      ro.disconnect();
      onData.dispose();
      ws?.close();
      term.dispose();
      termRef.current = null;
    };
  }, [sessionId, active]);

  return <div className="terminal" ref={containerRef} />;
}
