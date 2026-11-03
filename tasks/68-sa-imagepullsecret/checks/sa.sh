#!/usr/bin/env bash
set -euo pipefail
NAME=$(kubectl -n arch-pull68 get sa puller -o jsonpath='{.imagePullSecrets[0].name}')
[ "$NAME" = "regcred" ]
exit 0
