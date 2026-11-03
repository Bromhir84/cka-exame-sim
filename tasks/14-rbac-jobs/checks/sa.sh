#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-jobs get sa job-runner >/dev/null
