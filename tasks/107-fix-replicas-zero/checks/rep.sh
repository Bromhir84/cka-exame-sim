#!/usr/bin/env bash
set -euo pipefail
R=$(kubectl -n ts-rep107 get deploy web -o jsonpath='{.spec.replicas}')
[ "$R" = "2" ]
exit 0
