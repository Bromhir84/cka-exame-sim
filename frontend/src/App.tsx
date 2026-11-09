import { useCallback, useEffect, useRef, useState } from "react";
import {
  activateSessionTask,
  endSession,
  fetchBankSummary,
  finishSessionTask,
  getSession,
  getSessionTasks,
  setScreenLockHold,
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
  const [clockHeld, setClockHeld] = useState(false);
  const [clusterWait, setClusterWait] = useState(false);
  const hiddenAtRef = useRef(0);
  const examStatusRef = useRef(session?.status);
  examStatusRef.current = session?.status;
  const phaseRef = useRef(phase);
  phaseRef.current = phase;
  const phaseIsFinished = () => phaseRef.current === "finished";
  const pollGen = useRef(0);
  const sawSwitchingRef = useRef(false);

  const noteClusterSession = (next: Session) => {
    if (next.status === "switching") sawSwitchingRef.current = true;
    if (
      next.status === "done" ||
      next.status === "error" ||
      (next.status === "ready" && sawSwitchingRef.current)
    ) {
      sawSwitchingRef.current = false;
      setClusterWait(false);
    }
  };

  const beginClusterWait = () => {
    sawSwitchingRef.current = false;
    setClusterWait(true);
  };

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
          if (
            s.status === "ready" ||
            s.status === "provisioning" ||
            s.status === "switching"
          ) {
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
    if (!session) return;
    if (phaseIsFinished() || session.status === "done") return;
    const prefetchWatch = !!session.prefetch?.task_id;
    const heavy =
      session.status === "provisioning" ||
      session.status === "switching" ||
      clusterWait;
    // Also poll lightly while ready so next-cluster prefetch labels refresh.
    if (!heavy && !(session.status === "ready" && prefetchWatch)) {
      return;
    }
    const gen = ++pollGen.current;
    const id = window.setInterval(async () => {
      try {
        const s = await getSession(session.session_id);
        if (gen !== pollGen.current) return;
        if (phaseIsFinished()) return;
        const current = examStatusRef.current;
        if (
          (current === "grading" || current === "done") &&
          s.status !== "grading" &&
          s.status !== "done" &&
          s.status !== "error"
        ) {
          return;
        }
        const arrivedFromWait =
          sawSwitchingRef.current ||
          session.status === "switching" ||
          session.status === "provisioning";
        noteClusterSession(s);
        if (s.status === "done" && s.score) {
          setScore(s.score);
          setPhase("finished");
        }
        setSession(s);
        if (
          arrivedFromWait &&
          s.status === "ready" &&
          !phaseIsFinished()
        ) {
          const t = await getSessionTasks(s.session_id);
          if (gen !== pollGen.current || phaseIsFinished()) return;
          setTasks(t);
          setSelectedId(s.active_task_id ?? selectedId ?? t[0]?.id ?? null);
          setPhase("exam");
          const finishing = (session.progress?.label || "")
            .toLowerCase()
            .includes("finish");
          pushToast(
            finishing
              ? "Question finished"
              : session.status === "switching" || clusterWait
                ? "Question cluster ready"
                : "Exam environment ready",
            "ok"
          );
        }
        if (s.status === "error") {
          setError(s.error || "Provisioning failed");
          setPhase("lobby");
          setClusterWait(false);
          localStorage.removeItem(SESSION_KEY);
          pushToast(s.error || "Provisioning failed", "error");
        }
      } catch (e) {
        if (gen !== pollGen.current) return;
        setError(String((e as Error).message || e));
      }
    }, heavy ? 2000 : 4000);
    return () => {
      pollGen.current += 1;
      window.clearInterval(id);
    };
  }, [session, clusterWait, pushToast, selectedId]);

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
    if (s.status === "ready" || s.status === "switching") {
      const t = await getSessionTasks(s.session_id);
      setTasks(t);
      setSelectedId(s.active_task_id ?? t[0]?.id ?? null);
    }
  };

  const onSelectTask = async (taskId: string) => {
    if (!session || taskId === selectedId) return;
    if (session.status !== "ready") return;
    setError(null);
    // Finished questions: view prompt only (no cluster to open)
    if ((session.finished_task_ids ?? []).includes(taskId)) {
      setSelectedId(taskId);
      return;
    }
    setSelectedId(taskId);
    beginClusterWait();
    try {
      // Returns immediately; poll effect watches status=switching → ready.
      // The clock pauses as soon as this screen is requested, not after the
      // response, so a stale poll cannot keep it running on the switch window.
      const s = await activateSessionTask(session.session_id, taskId);
      noteClusterSession(s);
      if (s.status !== "switching") setClusterWait(false);
      setSession(s);
      setSelectedId(taskId);
      pushToast("Switching question cluster…", "ok");
    } catch (e) {
      const msg = String((e as Error).message || e);
      setClusterWait(false);
      sawSwitchingRef.current = false;
      setError(msg);
      pushToast(msg, "error");
      try {
        const s = await getSession(session.session_id);
        setSession(s);
        setSelectedId(s.active_task_id ?? selectedId);
      } catch {
        /* ignore */
      }
    }
  };

  const onFinishTask = async (taskId: string) => {
    if (!session || session.status !== "ready") return;
    setError(null);
    beginClusterWait();
    try {
      const s = await finishSessionTask(session.session_id, taskId);
      noteClusterSession(s);
      if (s.status !== "switching") setClusterWait(false);
      setSession(s);
      pushToast(
        "Question finished — grade saved (hidden until End Exam)",
        "ok"
      );
    } catch (e) {
      const msg = String((e as Error).message || e);
      setClusterWait(false);
      sawSwitchingRef.current = false;
      setError(msg);
      pushToast(msg, "error");
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

  const returnToStart = useCallback(() => {
    localStorage.removeItem(SESSION_KEY);
    pollGen.current += 1;
    sawSwitchingRef.current = false;
    setClusterWait(false);
    setPhase("lobby");
    setSession(null);
    setTasks([]);
    setSelectedId(null);
    setScore(null);
    setEnding(false);
    setError(null);
  }, []);

  useEffect(() => {
    if (phase !== "exam" || !session) return;
    const sessionId = session.session_id;
    let alive = true;

    const syncLock = (hold: boolean) => {
      const status = examStatusRef.current;
      if (status === "grading" || status === "done" || status === "error") return;
      if (hold) {
        if (!hiddenAtRef.current) hiddenAtRef.current = Date.now();
        setClockHeld(true);
        void fetch(`/api/sessions/${sessionId}/screen-lock`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ hold: true, extend_seconds: 0 }),
          keepalive: true,
        });
        return;
      }
      const started = hiddenAtRef.current;
      hiddenAtRef.current = 0;
      const waited = started ? Math.max(0, (Date.now() - started) / 1000) : 0;
      void (async () => {
        let restored: Session | null = null;
        let missing = false;
        for (let attempt = 0; attempt < 5 && alive; attempt += 1) {
          try {
            restored = await setScreenLockHold(sessionId, false, waited);
            break;
          } catch (e) {
            const msg = String((e as Error).message || e).toLowerCase();
            if (msg.includes("session not found")) {
              missing = true;
              break;
            }
            await new Promise((r) => window.setTimeout(r, 1000 * (attempt + 1)));
          }
        }
        if (!alive) return;
        if (missing) {
          returnToStart();
          setError(
            "The exam session ended while the computer was locked. Start again."
          );
          return;
        }
        if (restored) setSession(restored);
        else if (waited > 0) {
          setSession((prev) => {
            if (!prev?.ends_at) return prev;
            const ends = new Date(
              new Date(prev.ends_at).getTime() + waited * 1000
            ).toISOString();
            return {
              ...prev,
              ends_at: ends,
              remaining_seconds: Math.round((prev.remaining_seconds ?? 0) + waited),
            };
          });
        }
        setClockHeld(false);
      })();
    };

    if (document.visibilityState === "hidden") syncLock(true);
    const onVis = () => syncLock(document.visibilityState === "hidden");
    const onShow = () => {
      if (document.visibilityState === "visible") syncLock(false);
    };
    document.addEventListener("visibilitychange", onVis);
    window.addEventListener("pageshow", onShow);
    return () => {
      alive = false;
      document.removeEventListener("visibilitychange", onVis);
      window.removeEventListener("pageshow", onShow);
    };
  }, [phase, session?.session_id, returnToStart]);

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
      const report = await endSession(session.session_id, (next) => {
        // Publish the score together with status=done. Otherwise the exam
        // shell renders with no panel and the page looks blank.
        if (next.status === "done" && next.score) {
          setScore(next.score);
          setPhase("finished");
        }
        setSession(next);
      });
      setScore(report);
      setSession((prev) =>
        prev ? { ...prev, status: "done", score: report } : prev
      );
      setPhase("finished");
      setClusterWait(false);
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

  const report =
    score ?? (session?.status === "done" ? session.score ?? null : null);
  const showResults =
    Boolean(report) && (phase === "finished" || session?.status === "done");
  const showExam = phase === "exam" && Boolean(session) && !showResults;
  const showLobby = !showExam && !showResults;
  const switching = session?.status === "switching" || clusterWait;
  const ready = session?.status === "ready" && !switching;
  const showProgress = session?.status === "provisioning" || switching;
  const clockPaused =
    switching ||
    clockHeld ||
    Boolean(
      session?.timer_paused &&
        session.status !== "ready" &&
        session.status !== "grading" &&
        session.status !== "done"
    );

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

        {showExam && session && (
          <Timer
            endsAt={session.ends_at}
            remainingSeconds={session.remaining_seconds}
            paused={clockPaused}
            onExpire={finish}
          />
        )}

        <div className="top-actions">
          {showExam && (
            <button type="button" className="btn" onClick={toggleFullscreen}>
              Fullscreen
            </button>
          )}
          {showLobby && (
            <button
              type="button"
              className="btn primary"
              disabled={busy}
              onClick={onStart}
            >
              {busy ? "Starting…" : "Start Exam"}
            </button>
          )}
          {showExam && ready && (
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

      {showLobby && (
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

      {showExam && session && (
        <main
          className={ready ? "exam exam-shell" : "exam"}
          style={
            ready
              ? ({ ["--exam-left" as string]: `${leftPct}%` } as React.CSSProperties)
              : undefined
          }
        >
          {showProgress && (
            <div className="provisioning">
              <div className="spinner" />
              <p>
                {switching
                  ? "Switching question clusters…"
                  : "Setting up your exam environment…"}
                <br />
                <small>
                  {switching
                    ? "Previous work is kept. Returning to an opened question reconnects; a new question provisions a fresh cluster (a few minutes)."
                    : "Each question gets its own kind cluster. Cached images are loaded from this machine; the first cluster still takes a few minutes to boot."}
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
                  <span>{session.progress?.label || "Starting…"}</span>
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
                onSelect={onSelectTask}
                onFinish={onFinishTask}
                switching={switching}
                openedTaskIds={session.opened_task_ids ?? []}
                finishedTaskIds={session.finished_task_ids ?? []}
                prefetchLabel={session.prefetch?.label || null}
                prefetchTaskId={session.prefetch?.task_id ?? null}
              />
              <div
                className="exam-divider"
                onMouseDown={onDividerDown}
                role="separator"
                aria-orientation="vertical"
              />
              {session.active_task_id &&
              !(session.finished_task_ids ?? []).includes(
                session.active_task_id
              ) ? (
                <Workspace
                  key={`${session.session_id}-${session.active_task_id}`}
                  sessionId={session.session_id}
                  active={ready}
                />
              ) : (
                <div className="workspace workspace-empty">
                  <p>
                    No active cluster. Open another question, or press{" "}
                    <strong>End Exam</strong> to see your score.
                  </p>
                </div>
              )}
            </>
          )}
          {showExam &&
            session &&
            !showProgress &&
            !ready &&
            session.status !== "grading" && (
              <div className="provisioning">
                <p>This exam view is no longer available.</p>
                <button type="button" className="btn primary" onClick={returnToStart}>
                  Back to start
                </button>
              </div>
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

      {showResults && report && (
        <>
          <main className="lobby">
            <section className="lobby-hero">
              <h1>Exam complete</h1>
              <p>
                Your cluster has been torn down. Review your score, what missed,
                and the solutions, then start another attempt when ready.
              </p>
              <button
                type="button"
                className="btn primary lg"
                onClick={returnToStart}
              >
                Back to start
              </button>
            </section>
          </main>
          <ScoreReport score={report} onClose={returnToStart} />
        </>
      )}
    </div>
  );
}
