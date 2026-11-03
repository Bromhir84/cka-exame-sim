export type ToastItem = { id: number; message: string; kind?: "ok" | "error" };

type Props = { toasts: ToastItem[]; onDismiss: (id: number) => void };

export default function Toasts({ toasts, onDismiss }: Props) {
  if (!toasts.length) return null;
  return (
    <div className="toast-wrap" aria-live="polite">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`toast ${t.kind === "error" ? "error" : t.kind === "ok" ? "ok" : ""}`}
          onClick={() => onDismiss(t.id)}
          role="status"
        >
          {t.message}
        </div>
      ))}
    </div>
  );
}
