#!/usr/bin/env bash
set -euo pipefail
SC=$(kubectl get pv pv-host-95 -o jsonpath='{.spec.storageClassName}')
[ "$SC" = "manual-95" ]
RP=$(kubectl get pv pv-host-95 -o jsonpath='{.spec.persistentVolumeReclaimPolicy}')
[ "$RP" = "Retain" ]
exit 0
