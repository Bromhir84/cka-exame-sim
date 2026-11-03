#!/usr/bin/env bash
set -euo pipefail
NS=ts-selector
SEL=$(kubectl -n "$NS" get svc backend-svc -o jsonpath='{.spec.selector.app}')
[ "$SEL" = "backend" ]
EP=$(kubectl -n "$NS" get endpoints backend-svc -o jsonpath='{.subsets[0].addresses[0].ip}')
[ -n "$EP" ]
exit 0
