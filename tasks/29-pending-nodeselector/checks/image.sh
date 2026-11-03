#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n ts-pending get pod stuck -o jsonpath="{.spec.containers[0].image}")" = "nginx:1.27" ]
