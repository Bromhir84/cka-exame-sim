#!/usr/bin/env bash
set -euo pipefail
SA=$(kubectl -n arch-automount get sa no-token-sa -o jsonpath='{.automountServiceAccountToken}')
[ "$SA" = "false" ]
PODSA=$(kubectl -n arch-automount get pod quiet -o jsonpath='{.spec.serviceAccountName}')
[ "$PODSA" = "no-token-sa" ]
AUTO=$(kubectl -n arch-automount get pod quiet -o jsonpath='{.spec.automountServiceAccountToken}')
[ "$AUTO" = "false" ]
kubectl -n arch-automount wait --for=condition=Ready pod/quiet --timeout=120s
exit 0
