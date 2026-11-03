#!/usr/bin/env bash
set -euo pipefail
TYPE=$(kubectl -n arch-pull68 get secret regcred -o jsonpath='{.type}')
[ "$TYPE" = "kubernetes.io/dockerconfigjson" ]
exit 0
