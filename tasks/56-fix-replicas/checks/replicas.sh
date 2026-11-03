#!/usr/bin/env bash
set -euo pipefail
REP=$(kubectl -n ts-replicas get deploy frontend -o jsonpath='{.spec.replicas}')
[ "$REP" = "3" ]
exit 0
