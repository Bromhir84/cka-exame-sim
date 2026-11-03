#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n ts-probe get deploy web -o jsonpath="{.spec.template.spec.containers[0].readinessProbe.httpGet.path}")" = "/" ]
