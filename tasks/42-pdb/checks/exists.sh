#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-pdb get pdb api-pdb >/dev/null
exit 0
