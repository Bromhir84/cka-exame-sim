#!/usr/bin/env bash
set -euo pipefail
IMG=$(kubectl -n ts-pull get deploy web -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "nginx:1.27" ]
exit 0
