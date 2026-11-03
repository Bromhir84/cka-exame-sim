#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-secrets get rolebinding secret-reader-binding >/dev/null
