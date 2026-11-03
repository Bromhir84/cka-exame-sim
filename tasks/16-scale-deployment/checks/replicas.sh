#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n wl-scale get deploy api -o jsonpath="{.spec.replicas}")" = "4" ]
