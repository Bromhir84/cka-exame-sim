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

export type Session = {
  session_id: string;
  status: "provisioning" | "ready" | "grading" | "done" | "error";
  cluster_name: string;
  created_at: string;
  ends_at: string | null;
  remaining_seconds: number | null;
  error: string | null;
  score: ScoreReport | null;
  task_ids?: string[];
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

export async function startSession(): Promise<Session> {
  return json<Session>(
    await fetch("/api/sessions", { method: "POST" })
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

export async function endSession(id: string): Promise<ScoreReport> {
  return json<ScoreReport>(
    await fetch(`/api/sessions/${id}/end`, { method: "POST" })
  );
}

export function terminalWsUrl(sessionId: string): string {
  const proto = window.location.protocol === "https:" ? "wss" : "ws";
  return `${proto}://${window.location.host}/ws/terminal/${sessionId}`;
}
