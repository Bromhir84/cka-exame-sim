#!/usr/bin/env bash
set -euo pipefail
N=$(kubectl -n net-name89 get svc named -o jsonpath='{.spec.ports[0].name}')
[ "$N" = "http" ]
TP=$(kubectl -n net-name89 get svc named -o jsonpath='{.spec.ports[0].targetPort}')
[ "$TP" = "http" ]
exit 0
