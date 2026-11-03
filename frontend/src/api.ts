export type Task = {
  id: string;
  title: string;
  domain: string;
  domain_label: string;
  weight: number;
  prompt: string;
};

export type BankSummary = {
  count: number;
  slots: number;
  slot_weight_total: number;
  note: string;
  by_domain: Array<{
    domain: string;
    label: string;
    count: number;
    titles: string[];
  }>;
};

export type SessionProgress = {
  step: number;
  total: number;
  label: string;
  percent: number;
};

export type Session = {
  session_id: string;
  status:
    | "provisioning"
    | "switching"
    | "ready"
    | "grading"
    | "done"
    | "error";
  cluster_name: string;
  created_at: string;
  ends_at: string | null;
  remaining_seconds: number | null;
  error: string | null;
  score: ScoreReport | null;
  task_ids?: string[];
  domain?: string | null;
  desktop_url?: string | null;
  progress?: SessionProgress | null;
  active_task_id?: string | null;
  opened_task_ids?: string[];
  /** Graded + cluster removed; scores hidden until End Exam */
  finished_task_ids?: string[];
};

export type CheckResult = {
  id: string;
  description: string;
  weight: number;
  passed: boolean;
  earned: number;
  output?: string;
};

export type ScoreReport = {
  score: number;
  pass: boolean;
  pass_threshold: number;
  results: Array<{
    id: string;
    title: string;
    domain: string;
    domain_label: string;
    weight: number;
    passed: boolean;
    earned: number;
    checks?: CheckResult[];
    answers?: string | null;
  }>;
  domains: Array<{
    domain: string;
    label: string;
    earned: number;
    possible: number;
  }>;
};

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || res.statusText || "request failed");
  }
  return res.json() as Promise<T>;
}

export async function fetchBankSummary(): Promise<BankSummary> {
  return json<BankSummary>(await fetch("/api/tasks"));
}

export async function startSession(domain?: string | null): Promise<Session> {
  return json<Session>(
    await fetch("/api/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ domain: domain || null }),
    })
  );
}

export async function getSession(id: string): Promise<Session> {
  return json<Session>(await fetch(`/api/sessions/${id}`));
}

export async function getSessionTasks(id: string): Promise<Task[]> {
  const data = await json<{ tasks: Task[] }>(
    await fetch(`/api/sessions/${id}/tasks`)
  );
  return data.tasks;
}

export async function activateSessionTask(
  sessionId: string,
  taskId: string
): Promise<Session> {
  return json<Session>(
    await fetch(`/api/sessions/${sessionId}/activate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_id: taskId }),
    })
  );
}

export async function finishSessionTask(
  sessionId: string,
  taskId: string
): Promise<Session> {
  return json<Session>(
    await fetch(`/api/sessions/${sessionId}/finish-task`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_id: taskId }),
    })
  );
}

export async function startEndSession(id: string): Promise<Session> {
  return json<Session>(
    await fetch(`/api/sessions/${id}/end`, { method: "POST" })
  );
}

/** Start grading and poll until the score is ready (avoids gateway timeouts). */
export async function endSession(
  id: string,
  onUpdate?: (session: Session) => void
): Promise<ScoreReport> {
  let session = await startEndSession(id);
  onUpdate?.(session);
  if (session.status === "done" && session.score) {
    return session.score;
  }
  const deadline = Date.now() + 10 * 60 * 1000;
  while (Date.now() < deadline) {
    await new Promise((r) => setTimeout(r, 800));
    session = await getSession(id);
    onUpdate?.(session);
    if (session.status === "done" && session.score) {
      return session.score;
    }
    if (session.status === "ready" && session.error) {
      throw new Error(session.error);
    }
    if (session.status === "error") {
      throw new Error(session.error || "grading failed");
    }
  }
  throw new Error("Grading timed out — refresh and check session status");
}

export function terminalWsUrl(sessionId: string): string {
  const proto = window.location.protocol === "https:" ? "wss" : "ws";
  return `${proto}://${window.location.host}/ws/terminal/${sessionId}`;
}
