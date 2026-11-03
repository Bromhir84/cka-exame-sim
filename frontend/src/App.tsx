import { useCallback, useEffect, useState } from "react";
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
import Workspace from "./components/Workspace";

type Phase = "lobby" | "exam" | "finished";

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
  /** empty string = full exam; otherwise a domain key */
  const [domainFilter, setDomainFilter] = useState("");

  useEffect(() => {
    fetchBankSummary()
      .then(setBank)
      .catch((e) => setError(String(e.message || e)));
  }, []);

  // Poll while provisioning
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
        }
        if (s.status === "error") {
          setError(s.error || "Provisioning failed");
          setPhase("lobby");
        }
      } catch (e) {
        setError(String((e as Error).message || e));
      }
    }, 2500);
    return () => window.clearInterval(id);
  }, [session]);

  const onStart = async () => {
    setBusy(true);
    setError(null);
    setScore(null);
    try {
      const s = await startSession(domainFilter || null);
      setSession(s);
      setPhase("exam");
    } catch (e) {
      setError(String((e as Error).message || e));
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
    try {
      const report = await endSession(session.session_id);
      setScore(report);
      setSession((prev) =>
        prev ? { ...prev, status: "done", score: report } : prev
      );
      setPhase("finished");
    } catch (e) {
      setError(String((e as Error).message || e));
    } finally {
      setEnding(false);
    }
  }, [session, ending]);

  const ready = session?.status === "ready";

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
                  Full exam ({bank?.slots ?? 8} questions · all domains)
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
        <main className="exam">
          {session.status === "provisioning" && (
            <div className="provisioning">
              <div className="spinner" />
              <p>
                Provisioning kind cluster, Calico, and ingress…
                <br />
                <small>This often takes 2–5 minutes.</small>
              </p>
            </div>
          )}
          {ready && (
            <>
              <TaskPanel
                tasks={tasks}
                selectedId={selectedId}
                onSelect={setSelectedId}
              />
              <Workspace sessionId={session.session_id} active={ready} />
            </>
          )}
          {session.status === "grading" && (
            <div className="provisioning">
              <div className="spinner" />
              <p>Grading your cluster…</p>
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
                Your cluster has been torn down. Review your score, then start
                another attempt when ready.
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
          <ScoreReport
            score={score}
            onClose={() => {
              /* keep modal until they leave via lobby button; allow dismiss */
              setScore(null);
            }}
          />
        </>
      )}
    </div>
  );
}
