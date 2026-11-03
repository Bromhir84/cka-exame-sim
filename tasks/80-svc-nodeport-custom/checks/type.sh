#!/usr/bin/env bash
set -euo pipefail
T=$(kubectl -n net-np80 get svc web-np -o jsonpath='{.spec.type}')
[ "$T" = "NodePort" ]
exit 0
