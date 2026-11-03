#!/usr/bin/env bash
set -euo pipefail
R=$(kubectl -n wl-rs77 get rs web -o jsonpath='{.spec.replicas}')
[ "$R" = "4" ]
exit 0
