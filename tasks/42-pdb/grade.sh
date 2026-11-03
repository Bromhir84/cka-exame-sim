#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-pdb get pdb api-pdb >/dev/null
MIN=$(kubectl -n wl-pdb get pdb api-pdb -o jsonpath='{.spec.minAvailable}')
[ "$MIN" = "1" ]
SEL=$(kubectl -n wl-pdb get pdb api-pdb -o jsonpath='{.spec.selector.matchLabels.app}')
[ "$SEL" = "api" ]
exit 0
