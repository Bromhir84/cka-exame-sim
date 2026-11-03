#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-jobs get role job-runner-role -o json | grep -q '"jobs"'
kubectl -n arch-jobs get role job-runner-role -o json | grep -q '"batch"'
