#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n wl-cron get cronjob ping-cron -o jsonpath="{.spec.jobTemplate.spec.template.spec.containers[0].image}")" = "busybox:1.36" ]
