import { useEffect, useState } from "react";

type Props = {
  endsAt: string | null;
  remainingSeconds: number | null;
  paused?: boolean;
  onExpire: () => void;
};

function format(secs: number): string {
  const s = Math.max(0, secs);
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const r = s % 60;
  return [h, m, r].map((n) => String(n).padStart(2, "0")).join(":");
}

export default function Timer({
  endsAt,
  remainingSeconds,
  paused = false,
  onExpire,
}: Props) {
  const [left, setLeft] = useState(remainingSeconds ?? 0);

  useEffect(() => {
    if (paused || !endsAt) {
      setLeft((current) => {
        if (remainingSeconds == null) return paused ? current : 0;
        if (!paused || current <= 0) return remainingSeconds;
        // A poll must not walk the badge down while the switch screen is up.
        return Math.max(current, remainingSeconds);
      });
      return;
    }
    const tick = () => {
      const ms = new Date(endsAt).getTime() - Date.now();
      const secs = Math.max(0, Math.ceil(ms / 1000));
      setLeft(secs);
      if (secs <= 0) onExpire();
    };
    tick();
    const id = window.setInterval(tick, 1000);
    return () => window.clearInterval(id);
  }, [endsAt, remainingSeconds, paused, onExpire]);

  const urgent = !paused && left > 0 && left <= 300;

  return (
    <div
      className={`timer ${urgent ? "urgent" : ""} ${paused ? "paused" : ""}`}
      aria-live="polite"
    >
      <span>{format(left)}</span>
      {paused && <span className="timer-note">paused</span>}
    </div>
  );
}
