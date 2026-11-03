#!/usr/bin/env bash
set -euo pipefail
SA=$(kubectl -n arch-automount get sa no-token-sa -o jsonpath='{.automountServiceAccountToken}')
[ "$SA" = "false" ]
exit 0
