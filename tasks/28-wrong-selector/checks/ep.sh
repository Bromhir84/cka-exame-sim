#!/usr/bin/env bash
set -euo pipefail
EP=$(kubectl -n ts-selector get endpoints backend-svc -o jsonpath="{.subsets[0].addresses[0].ip}"); [ -n "$EP" ]
