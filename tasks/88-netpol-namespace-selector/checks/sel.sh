#!/usr/bin/env bash
set -euo pipefail
A=$(kubectl -n net-ns88 get networkpolicy allow-from-prod -o jsonpath='{.spec.podSelector.matchLabels.app}')
[ "$A" = "db" ]
exit 0
