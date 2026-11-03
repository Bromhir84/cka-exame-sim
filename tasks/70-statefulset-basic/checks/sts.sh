#!/usr/bin/env bash
set -euo pipefail
REP=$(kubectl -n wl-sts70 get sts web -o jsonpath='{.spec.replicas}')
[ "$REP" = "2" ]
SN=$(kubectl -n wl-sts70 get sts web -o jsonpath='{.spec.serviceName}')
[ "$SN" = "web" ]
kubectl -n wl-sts70 rollout status statefulset/web --timeout=180s
exit 0
