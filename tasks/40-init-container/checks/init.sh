#!/usr/bin/env bash
set -euo pipefail
INIT=$(kubectl -n wl-init get pod bootstrap -o jsonpath='{.spec.initContainers[0].name}')
[ "$INIT" = "setup" ]
IMG=$(kubectl -n wl-init get pod bootstrap -o jsonpath='{.spec.initContainers[0].image}')
[ "$IMG" = "busybox:1.36" ]
exit 0
