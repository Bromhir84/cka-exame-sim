import ReactMarkdown from "react-markdown";
import type { Task } from "../api";

type Props = {
  tasks: Task[];
  selectedId: string | null;
  onSelect: (id: string) => void;
};

export default function TaskPanel({ tasks, selectedId, onSelect }: Props) {
  const selected = tasks.find((t) => t.id === selectedId) ?? tasks[0];

  return (
    <div className="task-panel">
      <aside className="task-list">
        <h2>Questions</h2>
        <ol>
          {tasks.map((t, i) => (
            <li key={t.id}>
              <button
                type="button"
                className={selected?.id === t.id ? "active" : ""}
                onClick={() => onSelect(t.id)}
              >
                <span className="task-num">{i + 1}</span>
                <span className="task-meta">
                  <span className="task-title">{t.title}</span>
                  <span className="task-weight">
                    {t.weight}% · {t.domain}
                  </span>
                </span>
              </button>
            </li>
          ))}
        </ol>
      </aside>
      <article className="task-prompt">
        {selected ? (
          <ReactMarkdown>{selected.prompt}</ReactMarkdown>
        ) : (
          <p>No task selected.</p>
        )}
      </article>
    </div>
  );
}
