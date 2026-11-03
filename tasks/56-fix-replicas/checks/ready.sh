#!/usr/bin/env bash
set -euo pipefail
IMG=$(kubectl -n ts-replicas get deploy frontend -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "nginx:1.27" ]
kubectl -n ts-replicas rollout status deploy/frontend --timeout=120s
exit 0
