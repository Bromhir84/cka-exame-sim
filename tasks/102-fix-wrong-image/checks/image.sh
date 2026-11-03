#!/usr/bin/env bash
set -euo pipefail
IMG=$(kubectl -n ts-img102 get deploy site -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "nginx:1.27" ]
exit 0
