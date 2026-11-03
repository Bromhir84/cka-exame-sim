#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace stor-busy --dry-run=client -o yaml | kubectl apply -f -
if ! kubectl get sc standard >/dev/null 2>&1; then
  kubectl apply -f - <<'EOF'
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: rancher.io/local-path
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
EOF
fi
