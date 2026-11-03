#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-secrets get sa secret-reader >/dev/null
