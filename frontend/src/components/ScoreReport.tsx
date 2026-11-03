import { useState } from "react";
import ReactMarkdown from "react-markdown";
import type { ScoreReport as Score } from "../api";

type Props = {
  score: Score;
  onClose: () => void;
};

export default function ScoreReport({ score, onClose }: Props) {
  const [openAnswers, setOpenAnswers] = useState<Record<string, boolean>>({});

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

        <h3>By question</h3>
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
                      <span>
                        {c.passed ? "✓" : "✗"} {c.description}
                      </span>
                      <span>
                        {c.earned}/{c.weight}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
              {r.answers && (
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
                    {openAnswers[r.id] ? "Hide answer" : "Show answer"}
                  </button>
                  {openAnswers[r.id] && (
                    <div className="answer-md">
                      <ReactMarkdown>{r.answers}</ReactMarkdown>
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
