#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-crb get sa node-inspector >/dev/null
