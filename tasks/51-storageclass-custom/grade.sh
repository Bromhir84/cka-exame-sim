#!/usr/bin/env bash
set -euo pipefail
kubectl get storageclass fast-local >/dev/null
PROV=$(kubectl get storageclass fast-local -o jsonpath='{.provisioner}')
[ "$PROV" = "rancher.io/local-path" ]
RP=$(kubectl get storageclass fast-local -o jsonpath='{.reclaimPolicy}')
[ "$RP" = "Delete" ]
VBM=$(kubectl get storageclass fast-local -o jsonpath='{.volumeBindingMode}')
[ "$VBM" = "WaitForFirstConsumer" ]
SC=$(kubectl -n stor-sc-custom get pvc fast-pvc -o jsonpath='{.spec.storageClassName}')
[ "$SC" = "fast-local" ]
exit 0
