#!/usr/bin/env bash
set -euo pipefail
U=$(kubectl -n wl-sec75 get pod secure-pod -o jsonpath='{.spec.securityContext.runAsUser}')
[ "$U" = "1000" ]
G=$(kubectl -n wl-sec75 get pod secure-pod -o jsonpath='{.spec.securityContext.runAsGroup}')
[ "$G" = "3000" ]
exit 0
