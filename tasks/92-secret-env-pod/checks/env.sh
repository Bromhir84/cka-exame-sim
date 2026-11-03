#!/usr/bin/env bash
set -euo pipefail
U=$(kubectl -n stor-sec92 get pod sec-pod -o jsonpath='{.spec.containers[0].env[?(@.name=="DB_USER")].valueFrom.secretKeyRef.name}')
[ "$U" = "db-creds" ]
P=$(kubectl -n stor-sec92 get pod sec-pod -o jsonpath='{.spec.containers[0].env[?(@.name=="DB_PASS")].valueFrom.secretKeyRef.name}')
[ "$P" = "db-creds" ]
kubectl -n stor-sec92 wait --for=condition=Ready pod/sec-pod --timeout=120s
exit 0
