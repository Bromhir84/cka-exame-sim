#!/usr/bin/env bash
set -euo pipefail

NS=workloads-lab
[ "$(kubectl -n "$NS" get deploy web -o jsonpath='{.spec.replicas}')" = "3" ]
[ "$(kubectl -n "$NS" get deploy web -o jsonpath='{.spec.template.spec.containers[0].image}')" = "nginx:1.27" ]
kubectl -n "$NS" get deploy web -o yaml | grep -q 'configMapKeyRef'
kubectl -n "$NS" get deploy web -o yaml | grep -q 'secretKeyRef'
[ "$(kubectl -n "$NS" get deploy web -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}')" = "100m" ]
[ "$(kubectl -n "$NS" get deploy web -o jsonpath='{.spec.template.spec.containers[0].resources.requests.memory}')" = "64Mi" ]
