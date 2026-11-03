#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n wl-cron get cronjob ping-cron -o jsonpath="{.spec.schedule}")" = "*/5 * * * *" ]
[ "$(kubectl -n wl-cron get cronjob ping-cron -o jsonpath="{.spec.concurrencyPolicy}")" = "Forbid" ]
