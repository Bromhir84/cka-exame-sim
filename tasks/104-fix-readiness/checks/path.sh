#!/usr/bin/env bash
set -euo pipefail
P=$(kubectl -n ts-ready104 get deploy api -o jsonpath='{.spec.template.spec.containers[0].readinessProbe.httpGet.path}')
[ "$P" = "/" ]
exit 0
