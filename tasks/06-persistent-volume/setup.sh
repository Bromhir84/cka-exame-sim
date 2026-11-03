#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace storage-lab --dry-run=client -o yaml | kubectl apply -f -

# kind ships with a default StorageClass; ensure one named "standard" exists
if ! kubectl get sc standard >/dev/null 2>&1; then
  DEFAULT_SC=$(kubectl get sc -o jsonpath='{.items[?(@.metadata.annotations.storageclass\.kubernetes\.io/is-default-class=="true")].metadata.name}')
  if [ -n "${DEFAULT_SC:-}" ]; then
    kubectl get sc "$DEFAULT_SC" -o yaml \
      | sed "s/name: ${DEFAULT_SC}/name: standard/" \
      | grep -v 'uid:' | grep -v 'resourceVersion:' | grep -v 'creationTimestamp:' \
      | kubectl apply -f - || true
  fi
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
fi
