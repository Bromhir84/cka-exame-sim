#!/usr/bin/env bash
set -euo pipefail
kubectl get priorityclass high-priority-65 >/dev/null
exit 0
