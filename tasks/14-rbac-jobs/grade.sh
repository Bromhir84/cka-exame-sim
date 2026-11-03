#!/usr/bin/env bash
set -euo pipefail
NS=arch-jobs
kubectl -n "$NS" get sa job-runner >/dev/null
kubectl -n "$NS" get role job-runner-role -o json | grep -q '"jobs"'
kubectl -n "$NS" get role job-runner-role -o json | grep -q '"batch"'
kubectl -n "$NS" get rolebinding job-runner-binding >/dev/null
exit 0
