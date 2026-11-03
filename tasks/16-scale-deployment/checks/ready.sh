#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-scale rollout status deploy/api --timeout=120s
[ "$(kubectl -n wl-scale get deploy api -o jsonpath="{.status.readyReplicas}")" = "4" ]
