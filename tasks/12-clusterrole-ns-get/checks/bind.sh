#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-ns get sa ns-auditor >/dev/null
kubectl get clusterrolebinding ns-lister-binding -o jsonpath="{.roleRef.name}" | grep -qx ns-lister
