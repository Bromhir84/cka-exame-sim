#!/usr/bin/env bash
set -euo pipefail
NS=wl-probes
REP=$(kubectl -n "$NS" get deploy probed -o jsonpath='{.spec.replicas}')
[ "$REP" = "2" ]
RP=$(kubectl -n "$NS" get deploy probed -o jsonpath='{.spec.template.spec.containers[0].readinessProbe.httpGet.path}')
[ "$RP" = "/" ]
LP=$(kubectl -n "$NS" get deploy probed -o jsonpath='{.spec.template.spec.containers[0].livenessProbe.httpGet.path}')
[ "$LP" = "/" ]
kubectl -n "$NS" rollout status deploy/probed --timeout=120s
exit 0
