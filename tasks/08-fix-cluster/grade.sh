#!/usr/bin/env bash
set -euo pipefail

COREFILE=$(kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}')
echo "$COREFILE" | grep -q forward
echo "$COREFILE" | grep -qv notaplugin

kubectl -n kube-system rollout status deploy/coredns --timeout=180s
DESIRED=$(kubectl -n kube-system get deploy coredns -o jsonpath='{.spec.replicas}')
READY=$(kubectl -n kube-system get deploy coredns -o jsonpath='{.status.readyReplicas}')
[ "$READY" = "$DESIRED" ]

exit 0
