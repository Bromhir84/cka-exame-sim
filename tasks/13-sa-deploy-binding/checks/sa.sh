#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-sa-deploy get sa app-sa >/dev/null
