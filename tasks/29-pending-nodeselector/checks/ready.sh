#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-pending wait --for=condition=Ready pod/stuck --timeout=120s
