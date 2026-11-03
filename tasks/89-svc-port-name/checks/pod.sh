#!/usr/bin/env bash
set -euo pipefail
N=$(kubectl -n net-name89 get deploy api -o jsonpath='{.spec.template.spec.containers[0].ports[0].name}')
[ "$N" = "http" ]
exit 0
