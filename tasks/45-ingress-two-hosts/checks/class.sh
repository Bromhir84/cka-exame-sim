#!/usr/bin/env bash
set -euo pipefail
CLASS=$(kubectl -n net-twohost get ingress multi-ing -o jsonpath='{.spec.ingressClassName}')
[ "$CLASS" = "nginx" ]
exit 0
