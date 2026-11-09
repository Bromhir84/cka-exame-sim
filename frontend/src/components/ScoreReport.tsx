import { useState } from "react";
import ReactMarkdown from "react-markdown";
import type { CheckResult, ScoreReport as Score } from "../api";

type Props = {
  score: Score;
  onClose: () => void;
};

type Question = Score["results"][number];

function checkDetail(check: CheckResult): string {
  if (check.passed) return "";
  return (check.failure || check.output || "").trim();
}

function FailureDetail({ text }: { text: string }) {
  const notes: string[] = [];
  const body: string[] = [];
  for (const line of text.split("\n")) {
    if (line.startsWith("Likely mistake:")) notes.push(line);
    else body.push(line);
  }
  const prose = body.join("\n").trim();
  return (
    <>
      {prose ? <pre>{prose}</pre> : null}
      {notes.map((note, index) => (
        <p className="likely-mistake" key={`${index}-${note}`}>
          {note}
        </p>
      ))}
    </>
  );
}

function mistakes(result: Question): CheckResult[] {
  return (result.checks ?? []).filter((check) => checkDetail(check));
}

function wasGraded(result: Question): boolean {
  return (result.checks ?? []).some((check) => check.id !== "skipped");
}

export default function ScoreReport({ score, onClose }: Props) {
  const [openAnswers, setOpenAnswers] = useState<Record<string, boolean>>(() => {
    const next: Record<string, boolean> = {};
    for (const result of score.results) {
      const missed = result.earned !== result.weight && wasGraded(result);
      if (missed && (result.answers || mistakes(result).length)) {
        next[result.id] = true;
      }
    }
    return next;
  });
  const reviewIds = score.results
    .filter((result) => result.answers || mistakes(result).length > 0)
    .map((result) => result.id);
  const allOpen =
    reviewIds.length > 0 && reviewIds.every((id) => openAnswers[id]);

  const toggleAllAnswers = () => {
    if (allOpen) {
      setOpenAnswers({});
      return;
    }
    const next: Record<string, boolean> = {};
    for (const id of reviewIds) next[id] = true;
    setOpenAnswers(next);
  };

  return (
    <div className="modal-backdrop">
      <div className="modal score-modal" role="dialog" aria-labelledby="score-title">
        <h2 id="score-title">Exam Results</h2>
        <p className={`score-total ${score.pass ? "pass" : "fail"}`}>
          {score.score}%{" "}
          <span>{score.pass ? "PASS" : "FAIL"}</span>
          <small> (threshold {score.pass_threshold}%)</small>
        </p>

        <h3>By domain</h3>
        <ul className="domain-scores">
          {score.domains.map((d) => (
            <li key={d.domain}>
              <div className="domain-row">
                <span>{d.label}</span>
                <strong>
                  {d.earned}/{d.possible}
                </strong>
              </div>
              <div className="bar">
                <div
                  className="bar-fill"
                  style={{
                    width: `${d.possible ? (d.earned / d.possible) * 100 : 0}%`,
                  }}
                />
              </div>
            </li>
          ))}
        </ul>

        <div className="score-answers-toolbar">
          <h3>By question</h3>
          {reviewIds.length > 0 && (
            <button type="button" className="btn" onClick={toggleAllAnswers}>
              {allOpen ? "Hide all solutions" : "Show all solutions"}
            </button>
          )}
        </div>
        <ul className="task-scores detailed">
          {score.results.map((r) => (
            <li key={r.id} className={r.passed ? "ok" : "no"}>
              <div className="task-score-head">
                <span>
                  {r.earned === r.weight ? "PASS" : r.earned > 0 ? "PARTIAL" : "FAIL"}{" "}
                  — {r.title}
                </span>
                <span>
                  {r.earned}/{r.weight}
                </span>
              </div>
              {r.checks && r.checks.length > 0 && (
                <ul className="check-scores">
                  {r.checks.map((c) => (
                    <li key={c.id} className={c.passed ? "ok" : "no"}>
                      <div className="check-score-row">
                        <span>
                          {c.passed ? "✓" : "✗"} {c.description}
                        </span>
                        <span>
                          {c.earned}/{c.weight}
                        </span>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
              {(r.answers || mistakes(r).length > 0) && (
                <div className="answer-block">
                  <button
                    type="button"
                    className="btn"
                    onClick={() =>
                      setOpenAnswers((prev) => ({
                        ...prev,
                        [r.id]: !prev[r.id],
                      }))
                    }
                  >
                    {openAnswers[r.id]
                      ? mistakes(r).length
                        ? "Hide mistakes and solution"
                        : "Hide solution"
                      : mistakes(r).length
                        ? "Show mistakes and solution"
                        : "Show solution"}
                  </button>
                  {openAnswers[r.id] && (
                    <div className="review-panel">
                      {mistakes(r).length > 0 && (
                        <section className="failure-block">
                          <h4>What went wrong</h4>
                          <ul>
                            {mistakes(r).map((c) => (
                              <li key={c.id}>
                                <strong>{c.description}</strong>
                                <FailureDetail text={checkDetail(c)} />
                              </li>
                            ))}
                          </ul>
                        </section>
                      )}
                      {r.answers && (
                        <section className="answer-md">
                          <h4>Solution</h4>
                          <ReactMarkdown>{r.answers}</ReactMarkdown>
                        </section>
                      )}
                    </div>
                  )}
                </div>
              )}
            </li>
          ))}
        </ul>

        <button type="button" className="btn primary" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
}
