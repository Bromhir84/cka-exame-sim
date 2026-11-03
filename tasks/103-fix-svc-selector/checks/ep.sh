#!/usr/bin/env bash
set -euo pipefail
EP=$(kubectl -n ts-svc103 get endpoints web -o jsonpath='{.subsets[0].addresses[0].ip}')
[ -n "$EP" ]
exit 0
