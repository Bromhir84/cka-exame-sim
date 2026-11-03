#!/usr/bin/env bash
set -euo pipefail
# Require the actual fix (sleep command), not merely the pre-broken busybox image.
IMG=$(kubectl -n ts-crash get deploy looper -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "busybox:1.36" ]
FULL="$(kubectl -n ts-crash get deploy looper -o jsonpath='{.spec.template.spec.containers[0].command[*]}') $(kubectl -n ts-crash get deploy looper -o jsonpath='{.spec.template.spec.containers[0].args[*]}')"
echo "$FULL" | grep -q sleep
echo "$FULL" | grep -q 3600
