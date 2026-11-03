#!/usr/bin/env bash
set -euo pipefail
INIT=$(kubectl -n wl-init get pod bootstrap -o jsonpath='{.spec.initContainers[0].name}')
[ "$INIT" = "setup" ]
APP=$(kubectl -n wl-init get pod bootstrap -o jsonpath='{.spec.containers[0].name}')
[ "$APP" = "app" ]
kubectl -n wl-init wait --for=condition=Ready pod/bootstrap --timeout=120s
exit 0
