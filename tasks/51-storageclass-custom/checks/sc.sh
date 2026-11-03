#!/usr/bin/env bash
set -euo pipefail
PROV=$(kubectl get storageclass fast-local -o jsonpath='{.provisioner}')
[ "$PROV" = "rancher.io/local-path" ]
RP=$(kubectl get storageclass fast-local -o jsonpath='{.reclaimPolicy}')
[ "$RP" = "Delete" ]
VBM=$(kubectl get storageclass fast-local -o jsonpath='{.volumeBindingMode}')
[ "$VBM" = "WaitForFirstConsumer" ]
exit 0
