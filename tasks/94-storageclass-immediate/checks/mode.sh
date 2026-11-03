#!/usr/bin/env bash
set -euo pipefail
M=$(kubectl get sc fast-immediate -o jsonpath='{.volumeBindingMode}')
[ "$M" = "Immediate" ]
exit 0
