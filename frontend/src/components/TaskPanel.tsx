import ReactMarkdown from "react-markdown";
import type { Task } from "../api";

type Props = {
  tasks: Task[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onFinish?: (id: string) => void;
  switching?: boolean;
  openedTaskIds?: string[];
  finishedTaskIds?: string[];
  prefetchLabel?: string | null;
  prefetchTaskId?: string | null;
};

export default function TaskPanel({
  tasks,
  selectedId,
  onSelect,
  onFinish,
  switching = false,
  openedTaskIds = [],
  finishedTaskIds = [],
  prefetchLabel = null,
  prefetchTaskId = null,
}: Props) {
  const selected = tasks.find((t) => t.id === selectedId) ?? tasks[0];
  const index = Math.max(
    0,
    tasks.findIndex((t) => t.id === selected?.id)
  );
  const opened = new Set(openedTaskIds);
  const finished = new Set(finishedTaskIds);
  const selectedFinished = selected ? finished.has(selected.id) : false;
  const canFinish =
    !!selected &&
    !switching &&
    !selectedFinished &&
    opened.has(selected.id) &&
    !!onFinish;

  const goPrev = () => {
    if (index > 0) onSelect(tasks[index - 1].id);
  };
  const goNext = () => {
    if (index < tasks.length - 1) onSelect(tasks[index + 1].id);
  };

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
                disabled={switching}
                onClick={() => onSelect(t.id)}
              >
                <span className="task-num">{i + 1}</span>
                <span className="task-meta">
                  <span className="task-title">
                    {t.title}
                    {finished.has(t.id)
                      ? " · finished"
                      : opened.has(t.id)
                        ? " · cluster kept"
                        : prefetchTaskId === t.id
                          ? " · warming up"
                          : ""}
                  </span>
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
          <>
            <ReactMarkdown>{selected.prompt}</ReactMarkdown>
            <div className="task-nav">
              <button
                type="button"
                className="btn"
                disabled={switching || index <= 0}
                onClick={goPrev}
              >
                ← Previous
              </button>
              <span className="task-nav-pos">
                {index + 1} / {tasks.length}
              </span>
              <button
                type="button"
                className="btn primary"
                disabled={switching || index >= tasks.length - 1}
                onClick={goNext}
              >
                Next →
              </button>
            </div>
            <div className="task-finish-row">
              <button
                type="button"
                className="btn"
                disabled={!canFinish}
                onClick={() => selected && onFinish?.(selected.id)}
              >
                {selectedFinished ? "Finished" : "Finish question"}
              </button>
              <p className="task-nav-note task-finish-note">
                {selectedFinished
                  ? "Grade saved. Score stays hidden until you press End Exam."
                  : "Finish grades this question quietly, removes its cluster to free RAM, and keeps the result until End Exam."}
              </p>
            </div>
            {prefetchLabel ? (
              <p className="task-nav-note task-prefetch">{prefetchLabel}</p>
            ) : null}
            <p className="task-nav-note">
              Each question keeps its own kind cluster. Leaving parks it (work
              is preserved); returning reconnects. While you work, the next
              question’s cluster warms up in the background so Next is faster.
              Opening many questions uses more RAM.
            </p>
          </>
        ) : (
          <p>No task selected.</p>
        )}
      </article>
    </div>
  );
}
