#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-job get job pi-job >/dev/null
IMG=$(kubectl -n wl-job get job pi-job -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "busybox:1.36" ]
RP=$(kubectl -n wl-job get job pi-job -o jsonpath='{.spec.template.spec.restartPolicy}')
[ "$RP" = "Never" ]
BL=$(kubectl -n wl-job get job pi-job -o jsonpath='{.spec.backoffLimit}')
[ "$BL" = "2" ]
kubectl -n wl-job wait --for=condition=Complete job/pi-job --timeout=120s
exit 0
