#!/usr/bin/env bash
# Smoke-test API against a running backend (cluster provision may take minutes).
set -euo pipefail

API="${API:-http://localhost:8000}"

echo "== health =="
curl -fsS "$API/api/health" | tee /tmp/cka-health.json
echo

echo "== tasks =="
curl -fsS "$API/api/tasks" | tee /tmp/cka-tasks.json
echo

python3 - <<'PY'
import json
data=json.load(open("/tmp/cka-tasks.json"))
tasks=data["tasks"]
assert len(tasks)==8, tasks
assert sum(t["weight"] for t in tasks)==100
print(f"task count={len(tasks)} weight_sum=100 OK")
PY

echo "== start session =="
SID=$(curl -fsS -X POST "$API/api/sessions" | python3 -c 'import sys,json; print(json.load(sys.stdin)["session_id"])')
echo "session_id=$SID"

echo "== poll until ready/error (max ~10m) =="
for i in $(seq 1 120); do
  STATUS=$(curl -fsS "$API/api/sessions/$SID" | python3 -c 'import sys,json; print(json.load(sys.stdin)["status"])')
  echo "  [$i] status=$STATUS"
  if [ "$STATUS" = "ready" ]; then
    break
  fi
  if [ "$STATUS" = "error" ]; then
    curl -fsS "$API/api/sessions/$SID"
    exit 1
  fi
  sleep 5
done

curl -fsS "$API/api/sessions/$SID" | python3 -c 'import sys,json; s=json.load(sys.stdin); assert s["status"]=="ready", s'

echo "== end/grade session =="
curl -fsS -X POST "$API/api/sessions/$SID/end" | tee /tmp/cka-score.json
echo
python3 - <<'PY'
import json
s=json.load(open("/tmp/cka-score.json"))
assert "score" in s and "domains" in s and "results" in s
assert len(s["results"])==8
print(f"score={s['score']} pass={s['pass']} domains={len(s['domains'])}")
PY

echo "SMOKE OK"
