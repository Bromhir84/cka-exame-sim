#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-cm57 get role cm-reader-role >/dev/null
VERBS=$(kubectl -n arch-cm57 get role cm-reader-role -o jsonpath='{.rules[0].verbs[*]}')
echo "$VERBS" | grep -q get
echo "$VERBS" | grep -q list
RES=$(kubectl -n arch-cm57 get role cm-reader-role -o jsonpath='{.rules[0].resources[*]}')
echo "$RES" | grep -q configmaps
exit 0
