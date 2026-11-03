#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl get clusterrolebinding node-viewer-binding -o jsonpath="{.roleRef.name}")" = "node-viewer" ]
[ "$(kubectl get clusterrolebinding node-viewer-binding -o jsonpath="{.subjects[0].name}")" = "node-inspector" ]
