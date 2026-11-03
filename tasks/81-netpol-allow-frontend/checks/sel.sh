#!/usr/bin/env bash
set -euo pipefail
APP=$(kubectl -n net-np81 get networkpolicy allow-frontend -o jsonpath='{.spec.podSelector.matchLabels.app}')
[ "$APP" = "backend" ]
exit 0
