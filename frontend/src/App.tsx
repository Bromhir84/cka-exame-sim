import { useCallback, useEffect, useRef, useState } from "react";
import {
  endSession,
  fetchBankSummary,
  getSession,
  getSessionTasks,
  startSession,
  type BankSummary,
  type ScoreReport as Score,
  type Session,
  type Task,
} from "./api";
import ScoreReport from "./components/ScoreReport";
import TaskPanel from "./components/TaskPanel";
import Timer from "./components/Timer";
import Toasts, { type ToastItem } from "./components/Toasts";
import Workspace from "./components/Workspace";

type Phase = "lobby" | "exam" | "finished";

const SESSION_KEY = "cka-exam-session";
const PANEL_KEY = "cka-exam-left-pct";

function loadSavedSession(): { session_id: string } | null {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export default function App() {
  const [phase, setPhase] = useState<Phase>("lobby");
  const [bank, setBank] = useState<BankSummary | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [score, setScore] = useState<Score | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ending, setEnding] = useState(false);
  const [domainFilter, setDomainFilter] = useState("");
  const [resumeId, setResumeId] = useState<string | null>(null);
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const [leftPct, setLeftPct] = useState(() => {
    const v = Number(localStorage.getItem(PANEL_KEY) || "42");
    return Number.isFinite(v) ? Math.min(70, Math.max(25, v)) : 42;
  });
  const dragRef = useRef(false);
  const leftPctRef = useRef(leftPct);
  const toastId = useRef(1);
  const wakeLockRef = useRef<WakeLockSentinel | null>(null);

  const pushToast = useCallback((message: string, kind?: "ok" | "error") => {
    const id = toastId.current++;
    setToasts((prev) => [...prev, { id, message, kind }]);
    window.setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const loadBank = async () => {
      // Retry briefly: first open after install often races the API proxy.
      let lastErr: unknown = null;
      for (let i = 0; i < 15; i++) {
        try {
          const summary = await fetchBankSummary();
          if (!cancelled) {
            setBank(summary);
            setError(null);
          }
          return;
        } catch (e) {
          lastErr = e;
          await new Promise((r) => window.setTimeout(r, 1000));
        }
      }
      if (!cancelled) {
        setError(String((lastErr as Error)?.message || lastErr || "API unavailable"));
      }
    };
    void loadBank();

    const saved = loadSavedSession();
    if (saved?.session_id) {
      getSession(saved.session_id)
        .then((s) => {
          if (s.status === "ready" || s.status === "provisioning") {
            setResumeId(s.session_id);
          } else {
            localStorage.removeItem(SESSION_KEY);
          }
        })
        .catch(() => localStorage.removeItem(SESSION_KEY));
    }
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!session || session.status !== "provisioning") return;
    const id = window.setInterval(async () => {
      try {
        const s = await getSession(session.session_id);
        setSession(s);
        if (s.status === "ready") {
          const t = await getSessionTasks(s.session_id);
          setTasks(t);
          setSelectedId(t[0]?.id ?? null);
          setPhase("exam");
          pushToast("Exam environment ready", "ok");
        }
        if (s.status === "error") {
          setError(s.error || "Provisioning failed");
          setPhase("lobby");
          localStorage.removeItem(SESSION_KEY);
          pushToast(s.error || "Provisioning failed", "error");
        }
      } catch (e) {
        setError(String((e as Error).message || e));
      }
    }, 2500);
    return () => window.clearInterval(id);
  }, [session, pushToast]);

  // Wake Lock while exam ready
  useEffect(() => {
    const ready = session?.status === "ready" && phase === "exam";
    if (!ready) {
      wakeLockRef.current?.release().catch(() => undefined);
      wakeLockRef.current = null;
      return;
    }
    const request = async () => {
      try {
        if ("wakeLock" in navigator) {
          wakeLockRef.current = await navigator.wakeLock.request("screen");
        }
      } catch {
        /* unsupported / denied */
      }
    };
    void request();
    const onVis = () => {
      if (document.visibilityState === "visible") void request();
    };
    document.addEventListener("visibilitychange", onVis);
    return () => {
      document.removeEventListener("visibilitychange", onVis);
      wakeLockRef.current?.release().catch(() => undefined);
      wakeLockRef.current = null;
    };
  }, [session?.status, phase]);

  const attachSession = async (s: Session) => {
    setSession(s);
    localStorage.setItem(
      SESSION_KEY,
      JSON.stringify({ session_id: s.session_id, ends_at: s.ends_at })
    );
    setPhase("exam");
    if (s.status === "ready") {
      const t = await getSessionTasks(s.session_id);
      setTasks(t);
      setSelectedId(t[0]?.id ?? null);
    }
  };

  const onStart = async () => {
    setBusy(true);
    setError(null);
    setScore(null);
    setResumeId(null);
    try {
      const s = await startSession(domainFilter || null);
      await attachSession(s);
      pushToast("Provisioning cluster…", "ok");
    } catch (e) {
      const msg = String((e as Error).message || e);
      setError(msg);
      pushToast(msg, "error");
    } finally {
      setBusy(false);
    }
  };

  const onResume = async () => {
    if (!resumeId) return;
    setBusy(true);
    try {
      const s = await getSession(resumeId);
      await attachSession(s);
      pushToast("Resumed exam session", "ok");
      setResumeId(null);
    } catch (e) {
      localStorage.removeItem(SESSION_KEY);
      setResumeId(null);
      pushToast(String((e as Error).message || e), "error");
    } finally {
      setBusy(false);
    }
  };

  const selectedDomainMeta = bank?.by_domain.find(
    (d) => d.domain === domainFilter
  );
  const startLabel = busy
    ? "Provisioning cluster…"
    : domainFilter
      ? `Start ${selectedDomainMeta?.label ?? domainFilter} practice`
      : "Start 2-hour exam";

  const finish = useCallback(async () => {
    if (!session || ending) return;
    setEnding(true);
    setError(null);
    setSession((prev) =>
      prev
        ? {
            ...prev,
            status: "grading",
            progress: {
              step: 0,
              total: prev.task_ids?.length || tasks.length || 1,
              label: "Starting grading…",
              percent: 0,
            },
          }
        : prev
    );
    try {
      const report = await endSession(session.session_id, setSession);
      setScore(report);
      setSession((prev) =>
        prev ? { ...prev, status: "done", score: report } : prev
      );
      setPhase("finished");
      localStorage.removeItem(SESSION_KEY);
      pushToast(`Score: ${report.score}%`, report.pass ? "ok" : "error");
    } catch (e) {
      const msg = String((e as Error).message || e);
      setError(msg);
      pushToast(msg, "error");
      setSession((prev) => (prev ? { ...prev, status: "ready" } : prev));
    } finally {
      setEnding(false);
    }
  }, [session, ending, pushToast, tasks.length]);

  const ready = session?.status === "ready";

  const onDividerDown = (e: React.MouseEvent) => {
    e.preventDefault();
    dragRef.current = true;
    const onMove = (ev: MouseEvent) => {
      if (!dragRef.current) return;
      const pct = Math.min(70, Math.max(25, (ev.clientX / window.innerWidth) * 100));
      leftPctRef.current = pct;
      setLeftPct(pct);
    };
    const onUp = () => {
      dragRef.current = false;
      localStorage.setItem(PANEL_KEY, String(leftPctRef.current));
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
  };

  useEffect(() => {
    leftPctRef.current = leftPct;
    localStorage.setItem(PANEL_KEY, String(leftPct));
  }, [leftPct]);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen?.().catch(() => undefined);
    } else {
      document.exitFullscreen?.().catch(() => undefined);
    }
  };

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">CKA</span>
          <div>
            <strong>Exam Simulator</strong>
            <small>MVP practice environment</small>
          </div>
        </div>

        {phase !== "lobby" && session && (
          <Timer
            endsAt={session.ends_at}
            remainingSeconds={session.remaining_seconds}
            onExpire={finish}
          />
        )}

        <div className="top-actions">
          {phase === "exam" && (
            <button type="button" className="btn" onClick={toggleFullscreen}>
              Fullscreen
            </button>
          )}
          {phase === "lobby" && (
            <button
              type="button"
              className="btn primary"
              disabled={busy}
              onClick={onStart}
            >
              {busy ? "Starting…" : "Start Exam"}
            </button>
          )}
          {phase === "exam" && ready && (
            <button
              type="button"
              className="btn danger"
              disabled={ending}
              onClick={finish}
            >
              {ending ? "Grading…" : "End Exam"}
            </button>
          )}
        </div>
      </header>

      <Toasts
        toasts={toasts}
        onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))}
      />

      {resumeId && phase === "lobby" && (
        <div className="resume-banner">
          <span>An exam session is still active on this browser.</span>
          <button type="button" className="btn primary" onClick={onResume} disabled={busy}>
            Resume
          </button>
        </div>
      )}

      {error && <div className="banner error">{error}</div>}

      {phase === "lobby" && (
        <main className="lobby">
          <section className="lobby-hero">
            <h1>Certified Kubernetes Administrator</h1>
            <p>
              Timed practice against a real kind cluster. Choose a full exam
              (official domain weights) or focus on one domain. Pass hint: 66%.
            </p>

            <div className="domain-picker">
              <label htmlFor="domain-filter">Exam scope</label>
              <select
                id="domain-filter"
                value={domainFilter}
                disabled={busy}
                onChange={(e) => setDomainFilter(e.target.value)}
              >
                <option value="">
                  Full exam ({bank?.slots ?? 16} questions · all domains)
                </option>
                {(bank?.by_domain ?? []).map((d) => (
                  <option key={d.domain} value={d.domain}>
                    {d.label} only ({d.count} questions)
                  </option>
                ))}
              </select>
              <p className="lobby-note">
                {domainFilter
                  ? `Practice mode: all ${selectedDomainMeta?.count ?? ""} questions in this domain, weights equalized to 100%.`
                  : bank?.note}
              </p>
            </div>

            <button
              type="button"
              className="btn primary lg"
              disabled={busy}
              onClick={onStart}
            >
              {startLabel}
            </button>
          </section>
          <section className="lobby-tasks">
            <h2>Question bank</h2>
            <ul>
              {(bank?.by_domain ?? []).map((d) => (
                <li key={d.domain}>
                  <button
                    type="button"
                    className={`domain-pick-row ${
                      domainFilter === d.domain ? "active" : ""
                    }`}
                    disabled={busy}
                    onClick={() =>
                      setDomainFilter((prev) =>
                        prev === d.domain ? "" : d.domain
                      )
                    }
                  >
                    <span>{d.label}</span>
                    <span>{d.count} questions</span>
                  </button>
                </li>
              ))}
            </ul>
          </section>
        </main>
      )}

      {phase === "exam" && session && (
        <main
          className={ready ? "exam exam-shell" : "exam"}
          style={
            ready
              ? ({ ["--exam-left" as string]: `${leftPct}%` } as React.CSSProperties)
              : undefined
          }
        >
          {session.status === "provisioning" && (
            <div className="provisioning">
              <div className="spinner" />
              <p>
                Setting up your exam environment…
                <br />
                <small>
                  First run can take several minutes while images are pulled;
                  later starts are usually faster.
                </small>
              </p>
              <div
                className="progress-block"
                role="progressbar"
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={session.progress?.percent ?? 0}
                aria-label={session.progress?.label || "Provisioning"}
              >
                <div className="progress-meta">
                  <span>
                    {session.progress?.label || "Starting…"}
                  </span>
                  <span>
                    {session.progress
                      ? `${session.progress.step}/${session.progress.total}`
                      : ""}{" "}
                    · {session.progress?.percent ?? 0}%
                  </span>
                </div>
                <div className="progress-track">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${Math.min(100, session.progress?.percent ?? 0)}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          )}
          {ready && (
            <>
              <TaskPanel
                tasks={tasks}
                selectedId={selectedId}
                onSelect={setSelectedId}
              />
              <div
                className="exam-divider"
                onMouseDown={onDividerDown}
                role="separator"
                aria-orientation="vertical"
              />
              <Workspace
                sessionId={session.session_id}
                active={ready}
                desktopUrl={session.desktop_url ?? null}
              />
            </>
          )}
          {session.status === "grading" && (
            <div className="provisioning">
              <div className="spinner" />
              <p>
                Grading your cluster…
                <br />
                <small>Checking each question against the live environment.</small>
              </p>
              <div
                className="progress-block"
                role="progressbar"
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={session.progress?.percent ?? 0}
                aria-label={session.progress?.label || "Grading"}
              >
                <div className="progress-meta">
                  <span>{session.progress?.label || "Starting grading…"}</span>
                  <span>
                    {session.progress
                      ? `${session.progress.step}/${session.progress.total}`
                      : ""}{" "}
                    · {session.progress?.percent ?? 0}%
                  </span>
                </div>
                <div className="progress-track">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${Math.min(100, session.progress?.percent ?? 0)}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          )}
        </main>
      )}

      {phase === "finished" && score && (
        <>
          <main className="lobby">
            <section className="lobby-hero">
              <h1>Exam complete</h1>
              <p>
                Your cluster has been torn down. Review your score and answers,
                then start another attempt when ready.
              </p>
              <button
                type="button"
                className="btn primary lg"
                onClick={() => {
                  setPhase("lobby");
                  setSession(null);
                  setTasks([]);
                  setScore(null);
                }}
              >
                Back to lobby
              </button>
            </section>
          </main>
          <ScoreReport score={score} onClose={() => setScore(null)} />
        </>
      )}
    </div>
  );
}
