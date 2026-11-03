#!/usr/bin/env bash
set -euo pipefail
P=$(kubectl -n ts-live112 get deploy api -o jsonpath='{.spec.template.spec.containers[0].livenessProbe.httpGet.path}')
[ "$P" = "/" ]
exit 0
