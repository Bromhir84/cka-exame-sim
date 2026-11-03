#!/usr/bin/env bash
set -euo pipefail
# Require removing the impossible nodeSelector (image alone was already correct).
IMG=$(kubectl -n ts-pending get pod stuck -o jsonpath='{.spec.containers[0].image}')
[ "$IMG" = "nginx:1.27" ]
BAD=$(kubectl -n ts-pending get pod stuck -o jsonpath='{.spec.nodeSelector.disktype}')
[ -z "$BAD" ]
