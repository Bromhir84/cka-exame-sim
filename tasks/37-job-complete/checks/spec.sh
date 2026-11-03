#!/usr/bin/env bash
set -euo pipefail
IMG=$(kubectl -n wl-job get job pi-job -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "busybox:1.36" ]
RP=$(kubectl -n wl-job get job pi-job -o jsonpath='{.spec.template.spec.restartPolicy}')
[ "$RP" = "Never" ]
BL=$(kubectl -n wl-job get job pi-job -o jsonpath='{.spec.backoffLimit}')
[ "$BL" = "2" ]
exit 0
