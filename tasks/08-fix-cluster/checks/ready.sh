#!/usr/bin/env bash
set -euo pipefail

kubectl -n kube-system rollout status deploy/coredns --timeout=180s
DESIRED=$(kubectl -n kube-system get deploy coredns -o jsonpath='{.spec.replicas}')
READY=$(kubectl -n kube-system get deploy coredns -o jsonpath='{.status.readyReplicas}')
[ "$READY" = "$DESIRED" ]
