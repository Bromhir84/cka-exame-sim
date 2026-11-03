#!/usr/bin/env bash
set -euo pipefail
S=$(kubectl -n wl-cron71 get cronjob tick -o jsonpath='{.spec.schedule}')
[ "$S" = "*/5 * * * *" ]
exit 0
