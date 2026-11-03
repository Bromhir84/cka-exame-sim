#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace stor-pvc91 --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-stor-pvc91
spec:
  capacity:
    storage: 2Gi
  accessModes: [ReadWriteOnce]
  storageClassName: ""
  hostPath:
    path: /tmp/pv-stor-pvc91
EOF
