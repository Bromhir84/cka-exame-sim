#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-taint108 --dry-run=client -o yaml | kubectl apply -f -
# Taint all nodes
for n in $(kubectl get nodes -o name); do
  kubectl taint "$n" dedicated=cka:NoSchedule --overwrite || true
done
kubectl -n ts-taint108 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: critical
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
EOF
