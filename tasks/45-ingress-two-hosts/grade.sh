#!/usr/bin/env bash
set -euo pipefail
kubectl -n net-twohost get ingress multi-ing >/dev/null
H1=$(kubectl -n net-twohost get ingress multi-ing -o jsonpath='{.spec.rules[0].host}')
H2=$(kubectl -n net-twohost get ingress multi-ing -o jsonpath='{.spec.rules[1].host}')
echo "$H1 $H2" | grep -q alpha.cka.local
echo "$H1 $H2" | grep -q beta.cka.local
CLASS=$(kubectl -n net-twohost get ingress multi-ing -o jsonpath='{.spec.ingressClassName}')
[ "$CLASS" = "nginx" ]
exit 0
