#!/usr/bin/env bash
set -euo pipefail
REF=$(kubectl get clusterrolebinding pv-viewer-binding -o jsonpath='{.roleRef.name}')
[ "$REF" = "pv-viewer" ]
exit 0
