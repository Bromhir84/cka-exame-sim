#!/usr/bin/env bash
set -euo pipefail

# Preserve a working CoreDNS ConfigMap as a backup candidates can inspect/copy
kubectl -n kube-system get configmap coredns -o yaml \
  | sed 's/name: coredns/name: coredns-backup/' \
  | grep -v 'uid:' | grep -v 'resourceVersion:' | grep -v 'creationTimestamp:' \
  | kubectl apply -f -

# Sabotage CoreDNS ConfigMap so DNS breaks
kubectl -n kube-system apply -f - <<'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns
  namespace: kube-system
data:
  Corefile: |
    .:53 {
        errors
        # broken on purpose — invalid plugin
        notaplugin
    }
EOF

kubectl -n kube-system rollout restart deploy/coredns || true
sleep 3
