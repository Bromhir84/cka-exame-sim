#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-jobs get rolebinding job-runner-binding >/dev/null
