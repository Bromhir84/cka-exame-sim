#!/usr/bin/env bash
set -euo pipefail
# set env --from creates individual env entries OR envFrom depending on kubectl version; accept either
JSON=$(kubectl -n wl-envfrom76 get deploy api -o json)
echo "$JSON" | grep -q app-config
kubectl -n wl-envfrom76 rollout status deploy/api --timeout=120s
exit 0
