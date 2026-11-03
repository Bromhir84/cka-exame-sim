#!/usr/bin/env bash
set -euo pipefail
REF=$(kubectl -n wl-env69 get deploy web -o jsonpath='{.spec.template.spec.containers[0].env[?(@.name=="PASSWORD")].valueFrom.secretKeyRef.name}')
[ "$REF" = "app-secret" ]
KEY=$(kubectl -n wl-env69 get deploy web -o jsonpath='{.spec.template.spec.containers[0].env[?(@.name=="PASSWORD")].valueFrom.secretKeyRef.key}')
[ "$KEY" = "PASSWORD" ]
kubectl -n wl-env69 rollout status deploy/web --timeout=120s
exit 0
