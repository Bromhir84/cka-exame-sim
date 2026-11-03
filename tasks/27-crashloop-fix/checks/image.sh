#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n ts-crash get deploy looper -o jsonpath="{.spec.template.spec.containers[0].image}")" = "busybox:1.36" ]
