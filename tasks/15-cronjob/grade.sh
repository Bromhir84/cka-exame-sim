#!/usr/bin/env bash
set -euo pipefail
NS=wl-cron
SCHED=$(kubectl -n "$NS" get cronjob ping-cron -o jsonpath='{.spec.schedule}')
[ "$SCHED" = "*/5 * * * *" ]
POL=$(kubectl -n "$NS" get cronjob ping-cron -o jsonpath='{.spec.concurrencyPolicy}')
[ "$POL" = "Forbid" ]
IMG=$(kubectl -n "$NS" get cronjob ping-cron -o jsonpath='{.spec.jobTemplate.spec.template.spec.containers[0].image}')
[ "$IMG" = "busybox:1.36" ]
exit 0
