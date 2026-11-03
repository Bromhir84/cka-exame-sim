#!/usr/bin/env bash
set -euo pipefail

NS=workloads-lab
kubectl -n "$NS" get cm app-config -o jsonpath='{.data.APP_ENV}' | grep -qx production
TOKEN=$(kubectl -n "$NS" get secret app-secret -o jsonpath='{.data.APP_TOKEN}' | base64 -d)
[ "$TOKEN" = "s3cr3t" ]

REPLICAS=$(kubectl -n "$NS" get deploy web -o jsonpath='{.spec.replicas}')
[ "$REPLICAS" = "3" ]
IMAGE=$(kubectl -n "$NS" get deploy web -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMAGE" = "nginx:1.27" ]

# env from cm/secret
kubectl -n "$NS" get deploy web -o yaml | grep -q 'name: APP_ENV'
kubectl -n "$NS" get deploy web -o yaml | grep -q 'name: APP_TOKEN'
kubectl -n "$NS" get deploy web -o yaml | grep -q 'configMapKeyRef'
kubectl -n "$NS" get deploy web -o yaml | grep -q 'secretKeyRef'

CPU=$(kubectl -n "$NS" get deploy web -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}')
MEM=$(kubectl -n "$NS" get deploy web -o jsonpath='{.spec.template.spec.containers[0].resources.requests.memory}')
[ "$CPU" = "100m" ]
[ "$MEM" = "64Mi" ]

kubectl -n "$NS" rollout status deploy/web --timeout=120s
READY=$(kubectl -n "$NS" get deploy web -o jsonpath='{.status.readyReplicas}')
[ "$READY" = "3" ]

exit 0
