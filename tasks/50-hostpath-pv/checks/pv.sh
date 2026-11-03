#!/usr/bin/env bash
set -euo pipefail
kubectl get pv hp-pv >/dev/null
SC=$(kubectl get pv hp-pv -o jsonpath='{.spec.storageClassName}')
[ "$SC" = "manual" ]
HP=$(kubectl get pv hp-pv -o jsonpath='{.spec.hostPath.path}')
[ "$HP" = "/tmp/cka-hp-pv" ]
exit 0
