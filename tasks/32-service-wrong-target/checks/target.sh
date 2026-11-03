#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n ts-target get svc echo-svc -o jsonpath="{.spec.ports[0].targetPort}")" = "8080" ]
