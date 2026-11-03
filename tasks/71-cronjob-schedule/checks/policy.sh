#!/usr/bin/env bash
set -euo pipefail
P=$(kubectl -n wl-cron71 get cronjob tick -o jsonpath='{.spec.concurrencyPolicy}')
[ "$P" = "Forbid" ]
exit 0
