#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-affinity get deploy placed >/dev/null
KEY=$(kubectl -n wl-affinity get deploy placed -o jsonpath='{.spec.template.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0].key}')
[ "$KEY" = "kubernetes.io/os" ]
VAL=$(kubectl -n wl-affinity get deploy placed -o jsonpath='{.spec.template.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0].values[0]}')
[ "$VAL" = "linux" ]
kubectl -n wl-affinity rollout status deploy/placed --timeout=120s
exit 0
