#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-ds get ds node-agent >/dev/null
IMG=$(kubectl -n wl-ds get ds node-agent -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "busybox:1.36" ]
exit 0
