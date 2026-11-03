#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-cm110 get cm app-cm -o jsonpath='{.data.app\.conf}' | grep -q .
exit 0
