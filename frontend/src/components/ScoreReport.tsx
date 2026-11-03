import type { ScoreReport as Score } from "../api";

type Props = {
  score: Score;
  onClose: () => void;
};

export default function ScoreReport({ score, onClose }: Props) {
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
        <ul className="task-scores">
          {score.results.map((r) => (
            <li key={r.id} className={r.passed ? "ok" : "no"}>
              <span>
                {r.passed ? "PASS" : "FAIL"} — {r.title}
              </span>
              <span>
                {r.earned}/{r.weight}
              </span>
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
