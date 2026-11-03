#!/usr/bin/env bash
set -euo pipefail
A=$(kubectl -n wl-ann79 get deploy annotated -o jsonpath='{.spec.template.metadata.annotations.cka\.exam/owner}')
[ "$A" = "team-a" ]
exit 0
