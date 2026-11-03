#!/usr/bin/env bash
set -euo pipefail
KEY=$(kubectl -n wl-affinity get deploy placed -o jsonpath='{.spec.template.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0].key}')
[ "$KEY" = "kubernetes.io/os" ]
VAL=$(kubectl -n wl-affinity get deploy placed -o jsonpath='{.spec.template.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0].values[0]}')
[ "$VAL" = "linux" ]
exit 0
