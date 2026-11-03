#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n ts-selector get svc backend-svc -o jsonpath="{.spec.selector.app}")" = "backend" ]
